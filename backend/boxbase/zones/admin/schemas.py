from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

# ---------------------------------------------------------------------------
# 公共基类
# ---------------------------------------------------------------------------


class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    phone: str | None = None
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str
    tenant_id: uuid.UUID | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    active_tenant_id: uuid.UUID


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class SwitchTenantRequest(BaseModel):
    tenant_id: uuid.UUID


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------


class UserResponse(OrmBase):
    id: uuid.UUID
    username: str
    email: str
    phone: str | None
    is_active: bool
    created_at: datetime


class UserMeResponse(OrmBase):
    id: uuid.UUID
    username: str
    email: str
    phone: str | None
    is_active: bool
    active_tenant_id: uuid.UUID | None
    is_superadmin: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Membership schemas
# ---------------------------------------------------------------------------


class MembershipResponse(OrmBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    is_default: bool
    joined_at: datetime | None
    created_at: datetime
    tenant_name: str | None = None
    tenant_slug: str | None = None


class InviteUserRequest(BaseModel):
    username_or_email: str


class UpdateMembershipRequest(BaseModel):
    status: str | None = None
    is_default: bool | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("active", "invited", "disabled"):
            raise ValueError("status must be one of: active, invited, disabled")
        return v


# ---------------------------------------------------------------------------
# Role / Permission schemas
# ---------------------------------------------------------------------------


class PermissionResponse(OrmBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    created_at: datetime


class RoleResponse(OrmBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    created_at: datetime


class CreateRoleRequest(BaseModel):
    name: str


class AssignPermissionsRequest(BaseModel):
    permission_ids: list[uuid.UUID]


# ---------------------------------------------------------------------------
# Admin schemas
# ---------------------------------------------------------------------------


class TenantResponse(OrmBase):
    id: uuid.UUID
    slug: str
    name: str
    is_system: bool
    created_at: datetime
