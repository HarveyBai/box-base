from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.exceptions import ErrorCode, ErrorResponse
from boxbase.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from boxbase.zones.admin.models.membership import Membership
from boxbase.zones.admin.models.membership_role import MembershipRole
from boxbase.zones.admin.models.refresh_token import RefreshToken
from boxbase.zones.admin.models.role import Role
from boxbase.zones.admin.models.tenant import Tenant
from boxbase.zones.admin.models.user import User
from boxbase.zones.admin.schemas import (
    LoginRequest,
    LogoutRequest,
    MembershipResponse,
    RefreshRequest,
    RegisterRequest,
    SwitchTenantRequest,
    TokenResponse,
)

# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------


def _make_token_response(
    user_id: uuid.UUID,
    active_tenant_id: uuid.UUID,
    jti: str,
    username: str,
) -> TokenResponse:
    access_token = create_access_token(
        user_id=user_id,
        active_tenant_id=active_tenant_id,
        username=username,
    )
    refresh_token = create_refresh_token(jti=jti, user_id=user_id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        active_tenant_id=active_tenant_id,
    )


def _raise(status_code: int, code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail=ErrorResponse(code=code, message=message).model_dump(),
    )


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


async def register(payload: RegisterRequest, db: AsyncSession) -> User:
    # 校验全局唯一：username
    result = await db.execute(select(User).where(User.username == payload.username))  # type: ignore[arg-type]
    if result.scalar_one_or_none():
        _raise(409, ErrorCode.USER_ALREADY_EXISTS, "Username already exists.")

    # 校验全局唯一：email
    result = await db.execute(select(User).where(User.email == payload.email))  # type: ignore[arg-type]
    if result.scalar_one_or_none():
        _raise(409, ErrorCode.USER_ALREADY_EXISTS, "Email already exists.")

    # 校验全局唯一：phone（仅非 None 时）
    if payload.phone:
        result = await db.execute(select(User).where(User.phone == payload.phone))  # type: ignore[arg-type]
        if result.scalar_one_or_none():
            _raise(409, ErrorCode.USER_ALREADY_EXISTS, "Phone already exists.")

    # 创建用户
    user = User(
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    await db.flush()  # 获取 user.id

    # 查系统租户
    result = await db.execute(select(Tenant).where(Tenant.is_system.is_(True)))  # type: ignore[arg-type]
    system_tenant = result.scalar_one_or_none()
    if not system_tenant:
        _raise(500, "SYSTEM_TENANT_NOT_FOUND", "System tenant not configured.")

    # 创建 membership
    membership = Membership(
        tenant_id=system_tenant.id,  # type: ignore[union-attr]
        user_id=user.id,  # type: ignore[union-attr]
        is_default=True,
        status="active",
        joined_at=datetime.now(UTC),
    )
    db.add(membership)
    await db.flush()

    # 查默认 member 角色并赋予
    result = await db.execute(select(Role).where(Role.tenant_id == system_tenant.id, Role.name == "member"))  # type: ignore[arg-type,union-attr]
    member_role = result.scalar_one_or_none()
    if member_role:
        db.add(
            MembershipRole(
                tenant_id=system_tenant.id,  # type: ignore[union-attr]
                membership_id=membership.id,  # type: ignore[union-attr]
                role_id=member_role.id,  # type: ignore[union-attr]
            )
        )

    await db.commit()
    await db.refresh(user)
    return user  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


async def login(payload: LoginRequest, db: AsyncSession) -> TokenResponse:
    # 查全局用户
    result = await db.execute(select(User).where(User.username == payload.username))  # type: ignore[arg-type]
    user = result.scalar_one_or_none()

    if not user or not user.is_active:  # type: ignore[union-attr]
        _raise(401, ErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials.")

    if not verify_password(payload.password, user.hashed_password):  # type: ignore[union-attr]
        _raise(401, ErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials.")

    # 查 active membership 列表
    _stmt = select(Membership).where(
        Membership.user_id == user.id,  # type: ignore[arg-type,union-attr]
        Membership.status == "active",
        Membership.deleted_at.is_(None),
    )
    result = await db.execute(_stmt)  # type: ignore[arg-type]
    memberships: list[Membership] = list(result.scalars().all())  # type: ignore[arg-type]

    if not memberships:
        _raise(401, ErrorCode.AUTH_INVALID_CREDENTIALS, "No active membership found.")

    # 定活跃租户：指定 > is_default > 唯一
    active_tenant_id: uuid.UUID | None = None
    if payload.tenant_id:
        matched = [m for m in memberships if m.tenant_id == payload.tenant_id]
        if not matched:
            _raise(401, ErrorCode.AUTH_INVALID_CREDENTIALS, "Tenant membership not found.")
        active_tenant_id = payload.tenant_id
    else:
        defaults = [m for m in memberships if m.is_default]
        if defaults:
            active_tenant_id = defaults[0].tenant_id
        elif len(memberships) == 1:
            active_tenant_id = memberships[0].tenant_id
        else:
            _raise(401, ErrorCode.AUTH_INVALID_CREDENTIALS, "Cannot determine active tenant.")

    # 签发 token
    assert active_tenant_id is not None  # 已在上方逻辑保证
    jti = str(uuid.uuid4())
    db.add(
        RefreshToken(
            tenant_id=active_tenant_id,
            user_id=user.id,  # type: ignore[union-attr]
            jti=jti,
            status="active",
            expires_at=datetime.now(UTC).replace(second=0, microsecond=0),  # 占位，实际有效期由 JWT 控制
        )
    )
    await db.commit()

    return _make_token_response(user.id, active_tenant_id, jti, user.username)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# refresh_token
# ---------------------------------------------------------------------------


async def refresh_token(payload: RefreshRequest, db: AsyncSession) -> TokenResponse:
    try:
        claims = decode_refresh_token(payload.refresh_token)
    except Exception:
        _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Invalid or expired refresh token.")

    jti = claims.get("jti")
    if not jti:
        _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Invalid token claims.")

    # 查 jti（不限 status，后面区分 active/revoked 处理）
    result = await db.execute(  # type: ignore[arg-type]
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.deleted_at.is_(None),
        )
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Token has been revoked or not found.")

    # ---- 并发宽限：rotation-revoked 且在窗口内 → 放行 ----
    from boxbase.core.config import settings

    if token_record.status == "revoked":  # type: ignore[union-attr]
        if token_record.revoked_reason != "rotation":  # type: ignore[union-attr]
            _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Token has been revoked.")
        rc = token_record.revoked_at  # type: ignore[union-attr]
        if rc is None:
            _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Token has been revoked.")
        # SQLite 可能返回无时区 datetime，统一补上 UTC
        if rc.tzinfo is None:  # type: ignore[union-attr]
            rc = rc.replace(tzinfo=UTC)  # type: ignore[union-attr]
        now = datetime.now(UTC)
        grace = float(settings.refresh_rotation_grace_seconds)
        if (now - rc).total_seconds() > grace:  # type: ignore[operator]
            _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Token has been revoked.")
        # 在宽限窗口内：并发容错，签发新 token pair（不修改原记录状态）
    else:
        # rotation：旧 jti → revoked（正常流程）
        token_record.status = "revoked"  # type: ignore[union-attr]
        token_record.revoked_at = datetime.now(UTC)  # type: ignore[union-attr]
        token_record.revoked_reason = "rotation"  # type: ignore[union-attr]
        await db.flush()

    # 查 username
    user_result = await db.execute(select(User).where(User.id == token_record.user_id))  # type: ignore[arg-type,union-attr]
    user = user_result.scalar_one_or_none()
    username = user.username if user else ""  # type: ignore[union-attr]

    # 新 jti
    new_jti = str(uuid.uuid4())
    db.add(
        RefreshToken(
            tenant_id=token_record.tenant_id,  # type: ignore[union-attr]
            user_id=token_record.user_id,  # type: ignore[union-attr]
            jti=new_jti,
            status="active",
            expires_at=token_record.expires_at,  # type: ignore[union-attr]
        )
    )
    await db.commit()

    return _make_token_response(token_record.user_id, token_record.tenant_id, new_jti, username)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# logout
# ---------------------------------------------------------------------------


async def logout(payload: LogoutRequest, db: AsyncSession) -> None:
    try:
        claims = decode_refresh_token(payload.refresh_token)
    except Exception:
        _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Invalid or expired refresh token.")

    jti = claims.get("jti")
    if not jti:
        _raise(401, ErrorCode.AUTH_INVALID_TOKEN, "Invalid token claims.")

    result = await db.execute(  # type: ignore[arg-type]
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.status == "active",
            RefreshToken.deleted_at.is_(None),
        )
    )
    token_record = result.scalar_one_or_none()
    if token_record:
        token_record.status = "revoked"  # type: ignore[union-attr]
        token_record.revoked_at = datetime.now(UTC)  # type: ignore[union-attr]
        token_record.revoked_reason = "logout"  # type: ignore[union-attr]
        await db.commit()


# ---------------------------------------------------------------------------
# switch_tenant
# ---------------------------------------------------------------------------


async def switch_tenant(
    payload: SwitchTenantRequest,
    current_user_id: uuid.UUID,
    current_jti: str | None,
    db: AsyncSession,
) -> TokenResponse:
    # 校验目标 membership 存在且 active
    result = await db.execute(  # type: ignore[arg-type]
        select(Membership).where(
            Membership.user_id == current_user_id,
            Membership.tenant_id == payload.tenant_id,
            Membership.status == "active",
            Membership.deleted_at.is_(None),
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        _raise(404, ErrorCode.MEMBERSHIP_NOT_FOUND, "Target tenant membership not found.")

    # rotation：旧 jti → revoked
    if current_jti:
        rt_result = await db.execute(  # type: ignore[arg-type]
            select(RefreshToken).where(
                RefreshToken.jti == current_jti,
                RefreshToken.status == "active",
                RefreshToken.deleted_at.is_(None),
            )
        )
        old_token = rt_result.scalar_one_or_none()
        if old_token:
            old_token.status = "revoked"  # type: ignore[union-attr]
            old_token.revoked_at = datetime.now(UTC)  # type: ignore[union-attr]
            old_token.revoked_reason = "rotation"  # type: ignore[union-attr]
            await db.flush()

    # 查 username
    user_result = await db.execute(select(User).where(User.id == current_user_id))  # type: ignore[arg-type]
    user = user_result.scalar_one_or_none()
    username = user.username if user else ""  # type: ignore[union-attr]

    # 新 jti
    new_jti = str(uuid.uuid4())
    db.add(
        RefreshToken(
            tenant_id=payload.tenant_id,
            user_id=current_user_id,
            jti=new_jti,
            status="active",
            expires_at=datetime.now(UTC),
        )
    )
    await db.commit()

    return _make_token_response(current_user_id, payload.tenant_id, new_jti, username)


# ---------------------------------------------------------------------------
# get_my_tenants
# ---------------------------------------------------------------------------


async def get_my_tenants(
    current_user_id: uuid.UUID,
    db: AsyncSession,
) -> list[MembershipResponse]:
    result = await db.execute(  # type: ignore[arg-type]
        select(Membership).where(
            Membership.user_id == current_user_id,
            Membership.status == "active",
            Membership.deleted_at.is_(None),
        )
    )
    memberships = result.scalars().all()

    # 为每条 membership 查询租户 name / slug
    response_list: list[MembershipResponse] = []
    for m in memberships:
        t_result = await db.execute(select(Tenant).where(Tenant.id == m.tenant_id))  # type: ignore[arg-type]
        tenant = t_result.scalar_one_or_none()
        resp = MembershipResponse.model_validate(m)
        resp.tenant_name = tenant.name if tenant else None  # type: ignore[union-attr]
        resp.tenant_slug = tenant.slug if tenant else None  # type: ignore[union-attr]
        response_list.append(resp)
    return response_list
