from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.exceptions import ErrorCode, ErrorResponse
from boxbase.zones.admin.models.membership import Membership
from boxbase.zones.admin.models.membership_role import MembershipRole
from boxbase.zones.admin.models.role import Role
from boxbase.zones.admin.models.user import User
from boxbase.zones.admin.schemas import (
    InviteUserRequest,
    MembershipResponse,
    UpdateMembershipRequest,
    UserMeResponse,
    UserResponse,
)


def _raise(status_code: int, code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail=ErrorResponse(code=code, message=message).model_dump(),
    )


async def get_me(
    current_user_id: uuid.UUID,
    active_tenant_id: uuid.UUID | None,
    is_superadmin: bool,
    db: AsyncSession,
) -> UserMeResponse:
    stmt = select(User).where(User.id == current_user_id)  # type: ignore[arg-type]
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        _raise(404, ErrorCode.USER_NOT_FOUND, "User not found.")
    assert user is not None
    return UserMeResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        active_tenant_id=active_tenant_id,
        is_superadmin=is_superadmin,
        created_at=user.created_at,
    )


async def list_users(
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[UserResponse]:
    stmt = (  # type: ignore[arg-type]
        select(User)
        .join(Membership, Membership.user_id == User.id)
        .where(
            Membership.tenant_id == current_tenant_id,
            Membership.status == "active",
            Membership.deleted_at.is_(None),
            User.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


async def invite_user(
    payload: InviteUserRequest,
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> MembershipResponse:
    # 按 username 或 email 查全局 User
    stmt = select(User).where(  # type: ignore[arg-type]
        (User.username == payload.username_or_email) | (User.email == payload.username_or_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        _raise(404, ErrorCode.USER_NOT_FOUND, "User not found.")
    assert user is not None

    # 检查 membership 是否已存在
    stmt2 = select(Membership).where(  # type: ignore[arg-type]
        Membership.user_id == user.id,
        Membership.tenant_id == current_tenant_id,
        Membership.deleted_at.is_(None),
    )
    result2 = await db.execute(stmt2)
    existing = result2.scalar_one_or_none()
    if existing:
        _raise(409, ErrorCode.MEMBERSHIP_ALREADY_EXISTS, "User already in this tenant.")

    # 创建 membership
    membership = Membership(
        tenant_id=current_tenant_id,
        user_id=user.id,
        is_default=False,
        status="active",
        joined_at=datetime.now(UTC),
    )
    db.add(membership)
    await db.flush()

    # 赋默认 member 角色
    stmt3 = select(Role).where(  # type: ignore[arg-type]
        Role.tenant_id == current_tenant_id,
        Role.name == "member",
    )
    result3 = await db.execute(stmt3)
    member_role = result3.scalar_one_or_none()
    if member_role:
        db.add(
            MembershipRole(
                tenant_id=current_tenant_id,
                membership_id=membership.id,
                role_id=member_role.id,
            )
        )

    await db.commit()
    await db.refresh(membership)
    return MembershipResponse.model_validate(membership)


async def update_membership(
    membership_id: uuid.UUID,
    payload: UpdateMembershipRequest,
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> MembershipResponse:
    stmt = select(Membership).where(  # type: ignore[arg-type]
        Membership.id == membership_id,
        Membership.tenant_id == current_tenant_id,
        Membership.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    if not membership:
        _raise(404, ErrorCode.MEMBERSHIP_NOT_FOUND, "Membership not found.")
    assert membership is not None

    if payload.status is not None:
        membership.status = payload.status
    if payload.is_default is not None:
        membership.is_default = payload.is_default

    await db.commit()
    await db.refresh(membership)
    return MembershipResponse.model_validate(membership)


async def remove_membership(
    membership_id: uuid.UUID,
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    stmt = select(Membership).where(  # type: ignore[arg-type]
        Membership.id == membership_id,
        Membership.tenant_id == current_tenant_id,
        Membership.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    if not membership:
        _raise(404, ErrorCode.MEMBERSHIP_NOT_FOUND, "Membership not found.")
    assert membership is not None

    membership.deleted_at = datetime.now(UTC)
    await db.commit()
