from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.dependencies import RequestContext, get_db
from boxbase.core.security import get_current_user
from boxbase.zones.admin import service
from boxbase.zones.admin.models.user import User
from boxbase.zones.admin.schemas import (
    LoginRequest,
    LogoutRequest,
    MembershipResponse,
    RefreshRequest,
    RegisterRequest,
    SwitchTenantRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await service.register(payload, db)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await service.login(payload, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await service.refresh_token(payload, db)


@router.post("/logout", status_code=204)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> None:
    await service.logout(payload, db)


@router.post("/switch-tenant", response_model=TokenResponse)
async def switch_tenant(
    payload: SwitchTenantRequest,
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await service.switch_tenant(payload, ctx.user_id, None, db)


@router.get("/tenants", response_model=list[MembershipResponse])
async def get_my_tenants(
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MembershipResponse]:
    return await service.get_my_tenants(ctx.user_id, db)
