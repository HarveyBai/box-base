"""BoxBase 安全模块：密码哈希、JWT 签发/解码、get_current_user 依赖。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.config import settings
from boxbase.database import get_db
from boxbase.dependencies import RequestContext
from boxbase.models.membership import Membership
from boxbase.models.refresh_token import RefreshToken
from boxbase.models.user import User

# --------------------------------------------------------------------------- #
# 密码哈希
# --------------------------------------------------------------------------- #

_password_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    """使用 argon2 哈希明文密码。"""
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    return _password_hash.verify(plain, hashed)


# --------------------------------------------------------------------------- #
# JWT 签发 / 解码
# --------------------------------------------------------------------------- #

_ALGORITHM = "HS256"
_bearer = HTTPBearer()


def create_access_token(
    user_id: uuid.UUID,
    active_tenant_id: uuid.UUID,
    username: str,
) -> str:
    """签发 access token（HS256，有效期来自 config）。

    Claims:
        sub: user_id（字符串）
        tid: active_tenant_id（字符串）
        usr: username（用于 superadmin short-circuit）
        exp: 过期时间
        iat: 签发时间
        type: "access"
    """
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tid": str(active_tenant_id),
        "usr": username,
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def create_refresh_token(jti: str, user_id: uuid.UUID) -> str:
    """签发 refresh token（HS256，有效期来自 config）。

    Claims:
        sub: user_id（字符串）
        jti: JWT ID（唯一，白名单存库）
        exp: 过期时间
        iat: 签发时间
        type: "refresh"
    """
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "jti": jti,
        "exp": expire,
        "iat": now,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """解码并校验 access token，返回 claims dict。

    Raises:
        HTTPException 401：token 无效、过期或类型不符。
    """
    try:
        claims = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if claims.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


def decode_refresh_token(token: str) -> dict[str, Any]:
    """解码并校验 refresh token，返回 claims dict。

    Raises:
        HTTPException 401：token 无效、过期或类型不符。
    """
    try:
        claims = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if claims.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


# --------------------------------------------------------------------------- #
# get_current_user 依赖
# --------------------------------------------------------------------------- #


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RequestContext:
    """FastAPI 依赖：解码 access token，返回 RequestContext。

    流程：
    1. 解码 access token，取 user_id / active_tenant_id / username
    2. 超管 short-circuit：若 username == settings.superadmin_username（非空），
       直接返回 is_superadmin=True，跳过 membership 校验
    3. 普通用户：校验该 user 在 active_tenant_id 确有 active membership
       （防止伪造 token 进入未加入的租户）
    4. 返回 RequestContext

    Raises:
        HTTPException 401：token 无效
        HTTPException 403：无 active membership
    """
    claims = decode_access_token(credentials.credentials)

    user_id = uuid.UUID(claims["sub"])
    active_tenant_id = uuid.UUID(claims["tid"])
    username: str = claims.get("usr", "")

    # 超管 short-circuit
    if settings.superadmin_username and username == settings.superadmin_username:
        return RequestContext(
            user_id=user_id,
            active_tenant_id=active_tenant_id,
            is_superadmin=True,
        )

    # 普通用户：校验 active membership
    stmt = select(Membership).where(
        Membership.user_id == user_id,
        Membership.tenant_id == active_tenant_id,
        Membership.status == "active",
        Membership.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active membership in the specified tenant",
        )

    return RequestContext(
        user_id=user_id,
        active_tenant_id=active_tenant_id,
        is_superadmin=False,
    )


# --------------------------------------------------------------------------- #
# refresh rotation 辅助
# --------------------------------------------------------------------------- #


async def rotate_refresh_token(
    old_jti: str,
    user_id: uuid.UUID,
    active_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[str, str]:
    """Refresh token rotation：撤销旧 jti，签发新 access + refresh。

    Args:
        old_jti: 旧 refresh token 的 jti（需已通过 decode_refresh_token 校验）
        user_id: 当前用户 UUID
        active_tenant_id: 当前活跃租户 UUID
        db: 异步数据库 session

    Returns:
        (new_access_token, new_refresh_token)

    Raises:
        HTTPException 401：旧 jti 不在白名单或已被撤销
    """
    # 查白名单
    stmt = select(RefreshToken).where(
        RefreshToken.jti == old_jti,
        RefreshToken.status == "active",
        RefreshToken.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    token_record = result.scalar_one_or_none()

    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 撤销旧 jti
    token_record.status = "revoked"
    token_record.updated_at = datetime.now(UTC)
    await db.flush()

    # 查 username（用于 access token claims）
    user_stmt = select(User).where(User.id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    username = user.username if user else ""

    # 签发新 token
    new_jti = str(uuid.uuid4())
    new_access = create_access_token(user_id, active_tenant_id, username)
    new_refresh = create_refresh_token(new_jti, user_id)

    # 写入新 refresh token 记录
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    new_record = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=active_tenant_id,
        user_id=user_id,
        jti=new_jti,
        status="active",
        expires_at=expires_at,
    )
    db.add(new_record)
    await db.flush()

    return new_access, new_refresh
