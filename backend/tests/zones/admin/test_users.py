"""admin zone 用户相关集成测试。

覆盖：get_me、list_users、invite_user、superadmin 端点、权限校验。
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.security import hash_password
from boxbase.zones.admin.models.user import User

# ============================================================================
# get_me
# ============================================================================


@pytest.mark.asyncio
async def test_get_me_success(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """正常获取当前用户信息 → 200 UserMeResponse，字段完整。"""
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["username"] == "testsuperadmin"
    assert body["email"] == "testsuperadmin@example.com"
    assert "id" in body
    assert "is_superadmin" in body
    assert body["is_superadmin"] is True


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient) -> None:
    """无 token 访问 → 401。"""
    response = await client.get("/api/users/me")
    assert response.status_code == 401, response.text


# ============================================================================
# list_users
# ============================================================================


@pytest.mark.asyncio
async def test_list_users_with_permission(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """superadmin（有 owner 角色 → 全部权限）可访问 → 200。"""
    response = await client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1


@pytest.mark.asyncio
async def test_list_users_no_permission(
    client: AsyncClient,
    normal_token: str,
) -> None:
    """普通用户（member 角色，无 user:read 权限）→ 403。"""
    response = await client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert response.status_code == 403, response.text


# ============================================================================
# invite_user
# ============================================================================


@pytest.mark.asyncio
async def test_invite_user_success(
    client: AsyncClient,
    superadmin_token: str,
    db_session: AsyncSession,
) -> None:
    """邀请全局存在但尚未加入当前租户的用户 → 201 MembershipResponse。

    直接通过 DB 创建一个无 membership 的用户，再用 API 邀请。
    """
    # 直接插入一个没有 membership 的用户
    new_user = User(
        id=uuid.uuid4(),
        username="invite_target",
        email="invite_target@example.com",
        hashed_password=hash_password("pass1234"),
        is_active=True,
    )
    db_session.add(new_user)
    await db_session.commit()

    response = await client.post(
        "/api/users",
        json={"username_or_email": "invite_target"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["user_id"] == str(new_user.id)


@pytest.mark.asyncio
async def test_invite_duplicate_user(
    client: AsyncClient,
    superadmin_token: str,
    db_session: AsyncSession,
) -> None:
    """重复邀请同一用户 → 409 MEMBERSHIP_ALREADY_EXISTS。"""
    # 创建新用户（无 membership）
    new_user = User(
        id=uuid.uuid4(),
        username="dup_invite_target",
        email="dup_invite_target@example.com",
        hashed_password=hash_password("pass1234"),
        is_active=True,
    )
    db_session.add(new_user)
    await db_session.commit()

    # 第一次邀请 → 成功
    resp1 = await client.post(
        "/api/users",
        json={"username_or_email": "dup_invite_target"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert resp1.status_code == 201, resp1.text

    # 第二次邀请 → 409
    response = await client.post(
        "/api/users",
        json={"username_or_email": "dup_invite_target"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "MEMBERSHIP_ALREADY_EXISTS"


# ============================================================================
# superadmin 端点
# ============================================================================


@pytest.mark.asyncio
async def test_superadmin_access_admin_tenants(
    client: AsyncClient,
    superadmin_token: str,
) -> None:
    """superadmin 可访问 /api/admin/tenants → 200。"""
    response = await client.get(
        "/api/admin/tenants",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1


@pytest.mark.asyncio
async def test_normal_user_blocked_admin(
    client: AsyncClient,
    normal_token: str,
) -> None:
    """普通用户访问 /api/admin/tenants → 403。"""
    response = await client.get(
        "/api/admin/tenants",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert response.status_code == 403, response.text
