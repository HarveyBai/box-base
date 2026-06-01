from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.dependencies import RequestContext, get_db
from boxbase.core.exceptions import ErrorCode, ErrorResponse
from boxbase.core.security import get_current_user
from boxbase.zones.admin.models.tenant import Tenant
from boxbase.zones.admin.models.user import User
from boxbase.zones.admin.schemas import CleanupResponse, TenantResponse, UserResponse
from boxbase.zones.admin.services.auth import cleanup_expired_refresh_tokens

router = APIRouter()


def _require_superadmin(ctx: RequestContext) -> RequestContext:
    if not ctx.is_superadmin:
        raise HTTPException(
            status_code=403,
            detail=ErrorResponse(
                code=ErrorCode.PERMISSION_DENIED,
                message="Superadmin access required.",
            ).model_dump(),
        )
    return ctx


@router.get("/admin/tenants", response_model=list[TenantResponse])
async def list_tenants(
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TenantResponse]:
    _require_superadmin(ctx)
    stmt = select(Tenant).where(Tenant.deleted_at.is_(None))  # type: ignore[arg-type]
    result = await db.execute(stmt)
    tenants = result.scalars().all()
    return [TenantResponse.model_validate(t) for t in tenants]


@router.get("/admin/users", response_model=list[UserResponse])
async def list_all_users(
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    _require_superadmin(ctx)
    stmt = select(User).where(User.deleted_at.is_(None))  # type: ignore[arg-type]
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post(
    "/admin/maintenance/cleanup-refresh-tokens",
    response_model=CleanupResponse,
)
async def cleanup_tokens(
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CleanupResponse:
    """删除所有已过期的 refresh token（仅限 superadmin）。"""
    _require_superadmin(ctx)
    deleted = await cleanup_expired_refresh_tokens(db)
    return CleanupResponse(deleted=deleted)
