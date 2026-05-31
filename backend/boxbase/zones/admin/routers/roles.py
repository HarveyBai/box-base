from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.dependencies import RequestContext, get_db, require_permission
from boxbase.zones.admin import service
from boxbase.zones.admin.schemas import (
    AssignPermissionsRequest,
    CreateRoleRequest,
    PermissionResponse,
    RoleResponse,
)

router = APIRouter()


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    ctx: RequestContext = Depends(require_permission("role:read")),
    db: AsyncSession = Depends(get_db),
) -> list[RoleResponse]:
    return await service.list_roles(ctx.active_tenant_id, db)


@router.post("/roles", status_code=201, response_model=RoleResponse)
async def create_role(
    payload: CreateRoleRequest,
    ctx: RequestContext = Depends(require_permission("role:write")),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    return await service.create_role(payload, ctx.active_tenant_id, db)


@router.put("/roles/{role_id}/permissions", response_model=RoleResponse)
async def assign_permissions(
    role_id: uuid.UUID,
    payload: AssignPermissionsRequest,
    ctx: RequestContext = Depends(require_permission("role:assign")),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    return await service.assign_permissions(role_id, payload, ctx.active_tenant_id, db)


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    ctx: RequestContext = Depends(require_permission("role:read")),
    db: AsyncSession = Depends(get_db),
) -> list[PermissionResponse]:
    return await service.list_permissions(ctx.active_tenant_id, db)
