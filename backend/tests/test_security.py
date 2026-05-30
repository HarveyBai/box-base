"""security 模块核心路径 + ORM filter helper 单测。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.config import settings
from boxbase.dependencies import apply_soft_delete_filter, apply_tenant_filter
from boxbase.models.membership import Membership
from boxbase.models.refresh_token import RefreshToken
from boxbase.models.user import User
from boxbase.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    rotate_refresh_token,
    verify_password,
)

pytestmark = pytest.mark.asyncio


# --------------------------------------------------------------------------- #
# 密码哈希
# --------------------------------------------------------------------------- #


def test_hash_password_then_verify_ok() -> None:
    hashed = hash_password("s3cret-pw")
    assert hashed != "s3cret-pw"
    assert verify_password("s3cret-pw", hashed) is True


def test_verify_password_wrong_fails() -> None:
    hashed = hash_password("s3cret-pw")
    assert verify_password("wrong-pw", hashed) is False


# --------------------------------------------------------------------------- #
# JWT 签发 / 解码
# --------------------------------------------------------------------------- #


def test_access_token_roundtrip() -> None:
    uid = uuid.uuid4()
    tid = uuid.uuid4()
    token = create_access_token(uid, tid, "alice")
    claims = decode_access_token(token)
    assert claims["sub"] == str(uid)
    assert claims["tid"] == str(tid)
    assert claims["usr"] == "alice"
    assert claims["type"] == "access"


def test_refresh_token_roundtrip() -> None:
    uid = uuid.uuid4()
    jti = str(uuid.uuid4())
    token = create_refresh_token(jti, uid)
    claims = decode_refresh_token(token)
    assert claims["sub"] == str(uid)
    assert claims["jti"] == jti
    assert claims["type"] == "refresh"


def test_decode_expired_access_token_raises() -> None:
    from fastapi import HTTPException

    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "tid": str(uuid.uuid4()),
        "usr": "bob",
        "exp": now - timedelta(minutes=1),
        "iat": now - timedelta(minutes=31),
        "type": "access",
    }
    expired = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        decode_access_token(expired)
    assert exc.value.status_code == 401


def test_decode_tampered_access_token_raises() -> None:
    from fastapi import HTTPException

    token = create_access_token(uuid.uuid4(), uuid.uuid4(), "carol")
    tampered = token[:-3] + "abc"
    with pytest.raises(HTTPException) as exc:
        decode_access_token(tampered)
    assert exc.value.status_code == 401


def test_decode_wrong_token_type_raises() -> None:
    from fastapi import HTTPException

    # 用 refresh token 去解 access，类型不符必败
    refresh = create_refresh_token(str(uuid.uuid4()), uuid.uuid4())
    with pytest.raises(HTTPException) as exc:
        decode_access_token(refresh)
    assert exc.value.status_code == 401


# --------------------------------------------------------------------------- #
# refresh rotation
# --------------------------------------------------------------------------- #


async def test_rotate_refresh_token_revokes_old(db_session: AsyncSession) -> None:
    uid = uuid.uuid4()
    tid = uuid.uuid4()
    old_jti = str(uuid.uuid4())

    # 准备：写入 user + 旧 refresh token
    user = User(
        id=uid,
        username="dave",
        email="dave@example.com",
        hashed_password=hash_password("pw"),
        is_active=True,
    )
    old_token = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tid,
        user_id=uid,
        jti=old_jti,
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add_all([user, old_token])
    await db_session.flush()

    # 执行 rotation
    new_access, new_refresh = await rotate_refresh_token(old_jti, uid, tid, db_session)
    assert new_access
    assert new_refresh

    # 旧 jti 已被撤销
    stmt = select(RefreshToken).where(RefreshToken.jti == old_jti)
    result = await db_session.execute(stmt)
    old = result.scalar_one()
    assert old.status == "revoked"

    # 新 refresh token 已入库且 active
    new_claims = decode_refresh_token(new_refresh)
    new_jti = new_claims["jti"]
    stmt2 = select(RefreshToken).where(RefreshToken.jti == new_jti)
    result2 = await db_session.execute(stmt2)
    new_rec = result2.scalar_one()
    assert new_rec.status == "active"


async def test_rotate_refresh_token_unknown_jti_raises(
    db_session: AsyncSession,
) -> None:
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await rotate_refresh_token(str(uuid.uuid4()), uuid.uuid4(), uuid.uuid4(), db_session)
    assert exc.value.status_code == 401


# --------------------------------------------------------------------------- #
# ORM filter helper
# --------------------------------------------------------------------------- #


async def test_apply_soft_delete_filter_excludes_deleted(
    db_session: AsyncSession,
) -> None:
    tid = uuid.uuid4()
    alive = Membership(
        id=uuid.uuid4(),
        tenant_id=tid,
        user_id=uuid.uuid4(),
        is_default=True,
        status="active",
    )
    deleted = Membership(
        id=uuid.uuid4(),
        tenant_id=tid,
        user_id=uuid.uuid4(),
        is_default=False,
        status="active",
        deleted_at=datetime.now(UTC),
    )
    db_session.add_all([alive, deleted])
    await db_session.flush()

    stmt = apply_soft_delete_filter(select(Membership), Membership)
    result = await db_session.execute(stmt)
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].id == alive.id


async def test_apply_tenant_filter_isolates_tenant(
    db_session: AsyncSession,
) -> None:
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    m_a = Membership(
        id=uuid.uuid4(),
        tenant_id=tenant_a,
        user_id=uuid.uuid4(),
        is_default=True,
        status="active",
    )
    m_b = Membership(
        id=uuid.uuid4(),
        tenant_id=tenant_b,
        user_id=uuid.uuid4(),
        is_default=True,
        status="active",
    )
    db_session.add_all([m_a, m_b])
    await db_session.flush()

    stmt = apply_tenant_filter(select(Membership), Membership, tenant_a)
    result = await db_session.execute(stmt)
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].tenant_id == tenant_a


# --------------------------------------------------------------------------- #
# decode_refresh_token 异常分支
# --------------------------------------------------------------------------- #


def test_decode_expired_refresh_token_raises() -> None:
    from fastapi import HTTPException

    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "jti": str(uuid.uuid4()),
        "exp": now - timedelta(minutes=1),
        "iat": now - timedelta(days=8),
        "type": "refresh",
    }
    expired = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        decode_refresh_token(expired)
    assert exc.value.status_code == 401


def test_decode_tampered_refresh_token_raises() -> None:
    from fastapi import HTTPException

    token = create_refresh_token(str(uuid.uuid4()), uuid.uuid4())
    tampered = token[:-3] + "xyz"
    with pytest.raises(HTTPException) as exc:
        decode_refresh_token(tampered)
    assert exc.value.status_code == 401


def test_decode_wrong_type_for_refresh_raises() -> None:
    from fastapi import HTTPException

    # 用 access token 去解 refresh，类型不符必败
    access = create_access_token(uuid.uuid4(), uuid.uuid4(), "eve")
    with pytest.raises(HTTPException) as exc:
        decode_refresh_token(access)
    assert exc.value.status_code == 401


# --------------------------------------------------------------------------- #
# get_current_user 三条路径
# --------------------------------------------------------------------------- #


async def test_get_current_user_superadmin_short_circuit(
    db_session: AsyncSession,
) -> None:
    """超管 username 命中 → is_superadmin=True，不查 DB。"""
    from fastapi.security import HTTPAuthorizationCredentials

    from boxbase.security import get_current_user

    uid = uuid.uuid4()
    tid = uuid.uuid4()
    token = create_access_token(uid, tid, settings.superadmin_username)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    ctx = await get_current_user(credentials=credentials, db=db_session)
    assert ctx.is_superadmin is True
    assert ctx.user_id == uid
    assert ctx.active_tenant_id == tid


async def test_get_current_user_normal_with_membership(
    db_session: AsyncSession,
) -> None:
    """普通用户 + 有效 active membership → 放行，is_superadmin=False。"""
    from fastapi.security import HTTPAuthorizationCredentials

    from boxbase.security import get_current_user

    uid = uuid.uuid4()
    tid = uuid.uuid4()

    user = User(
        id=uid,
        username="frank",
        email="frank@example.com",
        hashed_password=hash_password("pw"),
        is_active=True,
    )
    membership = Membership(
        id=uuid.uuid4(),
        tenant_id=tid,
        user_id=uid,
        is_default=True,
        status="active",
    )
    db_session.add_all([user, membership])
    await db_session.flush()

    token = create_access_token(uid, tid, "frank")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    ctx = await get_current_user(credentials=credentials, db=db_session)
    assert ctx.is_superadmin is False
    assert ctx.user_id == uid
    assert ctx.active_tenant_id == tid


async def test_get_current_user_no_membership_raises(
    db_session: AsyncSession,
) -> None:
    """普通用户 + 无 active membership → 抛 403。"""
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    from boxbase.security import get_current_user

    uid = uuid.uuid4()
    tid = uuid.uuid4()

    # 只建 user，不建 membership
    user = User(
        id=uid,
        username="grace",
        email="grace@example.com",
        hashed_password=hash_password("pw"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(uid, tid, "grace")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials=credentials, db=db_session)
    assert exc.value.status_code == 403
