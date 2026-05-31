from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.dependencies import RequestContext, get_db, require_permission
from boxbase.core.security import get_current_user
from boxbase.zones.admin import service
from boxbase.zones.admin.schemas import (
    InviteUserRequest,
    MembershipResponse,
    UpdateMembershipRequest,
    UserMeResponse,
    UserResponse,
)

router = APIRouter()


@router.get("/users/me", response_model=UserMeResponse)
async def get_me(
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserMeResponse:
    return await service.get_me(ctx.user_id, ctx.active_tenant_id, ctx.is_superadmin, db)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    ctx: RequestContext = Depends(require_permission("user:read")),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    return await service.list_users(ctx.active_tenant_id, db)


@router.post("/users", status_code=201, response_model=MembershipResponse)
async def invite_user(
    payload: InviteUserRequest,
    ctx: RequestContext = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
) -> MembershipResponse:
    return await service.invite_user(payload, ctx.active_tenant_id, db)


@router.patch("/memberships/{membership_id}", response_model=MembershipResponse)
async def update_membership(
    membership_id: uuid.UUID,
    payload: UpdateMembershipRequest,
    ctx: RequestContext = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
) -> MembershipResponse:
    return await service.update_membership(membership_id, payload, ctx.active_tenant_id, db)


@router.delete("/memberships/{membership_id}", status_code=204)
async def remove_membership(
    membership_id: uuid.UUID,
    ctx: RequestContext = Depends(require_permission("user:write")),
    db: AsyncSession = Depends(get_db),
) -> None:
    await service.remove_membership(membership_id, ctx.active_tenant_id, db)
