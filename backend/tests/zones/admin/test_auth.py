"""admin zone 认证相关集成测试。

覆盖：注册、登录、refresh、logout、安全场景。
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.zones.admin.conftest import (
    NORMAL_EMAIL,
    NORMAL_USERNAME,
    SUPERADMIN_PASSWORD,
    SUPERADMIN_USERNAME,
    SeedData,
    _make_access_token,
)

# ============================================================================
# 注册
# ============================================================================


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """注册新用户 → 201，返回 UserResponse。"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "pass1234",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["username"] == "newuser"
    assert body["email"] == "newuser@example.com"
    assert "id" in body


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient) -> None:
    """重复用户名注册 → 409 USER_ALREADY_EXISTS。"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": NORMAL_USERNAME,
            "email": "another@example.com",
            "password": "pass1234",
        },
    )
    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """重复邮箱注册 → 409 USER_ALREADY_EXISTS。"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "anotheruser",
            "email": NORMAL_EMAIL,
            "password": "pass1234",
        },
    )
    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "USER_ALREADY_EXISTS"


# ============================================================================
# 登录
# ============================================================================


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """正确凭据登录 → 200，返回 TokenResponse。"""
    assert SeedData.system_tenant is not None
    response = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["active_tenant_id"] == str(SeedData.system_tenant.id)


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    """错误密码登录 → 401 AUTH_INVALID_CREDENTIALS。"""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["code"] == "AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """不存在的用户登录 → 401 AUTH_INVALID_CREDENTIALS。"""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "whatever",
        },
    )
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["code"] == "AUTH_INVALID_CREDENTIALS"


# ============================================================================
# refresh
# ============================================================================


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient) -> None:
    """有效 refresh token → 200，返回新 TokenResponse。"""
    # 先登录获取 refresh_token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    refresh_token = login_resp.json()["refresh_token"]

    # 用 refresh_token 获取新 token
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    # 新 refresh_token 应不同于旧
    assert body["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_refresh_revoked_token(client: AsyncClient) -> None:
    """logout 后再 refresh → 401 AUTH_INVALID_TOKEN。"""
    # 登录
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    refresh_token = login_resp.json()["refresh_token"]

    # logout
    await client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )

    # 再 refresh
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


@pytest.mark.asyncio
async def test_refresh_tampered_token(client: AsyncClient) -> None:
    """篡改的 refresh token → 401 AUTH_INVALID_TOKEN。"""
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "not.a.valid.token"},
    )
    assert response.status_code == 401, response.text
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


# ============================================================================
# logout
# ============================================================================


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient) -> None:
    """正常 logout → 204，再 refresh 旧 token → 401。"""
    # 登录
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    refresh_token = login_resp.json()["refresh_token"]

    # logout
    logout_resp = await client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_resp.status_code == 204, logout_resp.text

    # 旧 refresh_token 应被撤销
    refresh_resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401


# ============================================================================
# 安全场景
# ============================================================================


@pytest.mark.asyncio
async def test_forged_tenant_id_rejected(client: AsyncClient) -> None:
    """伪造 active_tenant_id 进未加入租户 → 403。

    用普通用户的 user_id 签一个指向随机 tenant_id 的 token，
    签名合法但 get_current_user 校验 membership 时应拒绝。
    """
    assert SeedData.normal_user is not None

    fake_tenant_id = uuid.uuid4()
    forged_token = _make_access_token(
        SeedData.normal_user.id,
        fake_tenant_id,
        NORMAL_USERNAME,
    )

    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {forged_token}"},
    )
    assert response.status_code == 403, response.text
