"""admin zone 角色/权限相关集成测试。

覆盖：list_roles、create_role、assign_permissions、list_permissions、跨租户安全。
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.zones.admin.conftest import (
    NORMAL_USERNAME,
    SeedData,
    _make_access_token,
)

# ============================================================================
# list_roles
# ============================================================================


@pytest.mark.asyncio
async def test_list_roles_success(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """获取角色列表 → 200，返回默认 3 个角色。"""
    response = await client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 3
    names = {r["name"] for r in body}
    assert names == {"owner", "admin", "member"}


# ============================================================================
# create_role
# ============================================================================


@pytest.mark.asyncio
async def test_create_role_success(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """创建新角色 → 201 RoleResponse。"""
    response = await client.post(
        "/api/roles",
        json={"name": "editor"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "editor"
    assert "id" in body
    assert "tenant_id" in body


@pytest.mark.asyncio
async def test_create_role_duplicate(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """重复创建同名角色 → 409 ROLE_ALREADY_EXISTS。"""
    # 先创建一个
    await client.post(
        "/api/roles",
        json={"name": "editor"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    # 再创建同名
    response = await client.post(
        "/api/roles",
        json={"name": "editor"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "ROLE_ALREADY_EXISTS"


# ============================================================================
# assign_permissions
# ============================================================================


@pytest.mark.asyncio
async def test_assign_permissions_success(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """为角色分配权限 → 200 RoleResponse。"""
    assert SeedData.roles.get("admin") is not None
    assert SeedData.permissions.get("user:read") is not None

    admin_role = SeedData.roles["admin"]
    perm = SeedData.permissions["user:read"]

    response = await client.put(
        f"/api/roles/{admin_role.id}/permissions",
        json={"permission_ids": [str(perm.id)]},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == str(admin_role.id)


# ============================================================================
# list_permissions
# ============================================================================


@pytest.mark.asyncio
async def test_list_permissions_success(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """获取权限列表 → 200，返回默认 5 个权限。"""
    response = await client.get(
        "/api/permissions",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 5
    codes = {p["code"] for p in body}
    assert codes == {"user:read", "user:write", "role:read", "role:write", "role:assign"}


# ============================================================================
# 跨租户安全
# ============================================================================


@pytest.mark.asyncio
async def test_cross_tenant_blocked(
    client: AsyncClient,
    normal_token: str,
) -> None:
    """伪造 tenant_id token 访问其他租户资源 → 403。

    用普通用户签一个指向不存在租户的 token，验证 membership 校验拦截。
    """
    assert SeedData.normal_user is not None

    fake_tenant_id = uuid.uuid4()
    forged_token = _make_access_token(
        SeedData.normal_user.id,
        fake_tenant_id,
        NORMAL_USERNAME,
    )

    response = await client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {forged_token}"},
    )
    assert response.status_code == 403, response.text


# ---------------------------------------------------------------------------
# 补充：roles service 错误分支覆盖
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_assign_permissions_role_not_found(client: AsyncClient, superadmin_token: str) -> None:
    """给不存在的 role 分配权限 → 404"""
    resp = await client.put(
        f"/api/roles/{uuid.uuid4()}/permissions",
        json={"permission_ids": []},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_role_no_permission(client: AsyncClient, normal_token: str) -> None:
    """无 role:write 权限用户创建角色 → 403"""
    resp = await client.post(
        "/api/roles",
        json={"name": "hacker_role"},
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_roles_no_permission(client: AsyncClient, normal_token: str) -> None:
    """无 role:read 权限用户列角色 → 403"""
    resp = await client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert resp.status_code == 403
