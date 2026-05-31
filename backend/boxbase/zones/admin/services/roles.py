from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.exceptions import ErrorCode, ErrorResponse
from boxbase.zones.admin.models.permission import Permission
from boxbase.zones.admin.models.role import Role
from boxbase.zones.admin.models.role_permission import RolePermission
from boxbase.zones.admin.schemas import (
    AssignPermissionsRequest,
    CreateRoleRequest,
    PermissionResponse,
    RoleResponse,
)


def _raise(status_code: int, code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail=ErrorResponse(code=code, message=message).model_dump(),
    )


async def list_roles(
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[RoleResponse]:
    stmt = select(Role).where(  # type: ignore[arg-type]
        Role.tenant_id == current_tenant_id,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return [RoleResponse.model_validate(r) for r in roles]


async def create_role(
    payload: CreateRoleRequest,
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> RoleResponse:
    # 检查同名角色是否已存在
    stmt = select(Role).where(  # type: ignore[arg-type]
        Role.tenant_id == current_tenant_id,
        Role.name == payload.name,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        _raise(409, "ROLE_ALREADY_EXISTS", f"Role '{payload.name}' already exists.")

    role = Role(tenant_id=current_tenant_id, name=payload.name)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


async def assign_permissions(
    role_id: uuid.UUID,
    payload: AssignPermissionsRequest,
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> RoleResponse:
    # 校验 role 存在且属于当前租户
    stmt = select(Role).where(  # type: ignore[arg-type]
        Role.id == role_id,
        Role.tenant_id == current_tenant_id,
        Role.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        _raise(404, ErrorCode.ROLE_NOT_FOUND, "Role not found.")
    assert role is not None

    # 删除旧的 role_permissions
    await db.execute(  # type: ignore[arg-type]
        delete(RolePermission).where(RolePermission.role_id == role_id)
    )

    # 插入新的 role_permissions
    for perm_id in payload.permission_ids:
        db.add(
            RolePermission(
                tenant_id=current_tenant_id,
                role_id=role_id,
                permission_id=perm_id,
            )
        )

    await db.commit()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


async def list_permissions(
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[PermissionResponse]:
    stmt = select(Permission).where(  # type: ignore[arg-type]
        Permission.tenant_id == current_tenant_id,
        Permission.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    permissions = result.scalars().all()
    return [PermissionResponse.model_validate(p) for p in permissions]
