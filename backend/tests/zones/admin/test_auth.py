"""admin zone 认证相关集成测试。

覆盖：注册、登录、refresh、logout、安全场景。
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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


# ---------------------------------------------------------------------------
# 补充：auth service 错误分支覆盖
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_duplicate_phone(client: AsyncClient) -> None:
    """注册重复手机号 → 409"""
    phone = "+8613800000001"
    await client.post(
        "/api/auth/register",
        json={
            "username": "phoneuser1",
            "email": "phoneuser1@example.com",
            "phone": phone,
            "password": "password123",
        },
    )
    resp = await client.post(
        "/api/auth/register",
        json={
            "username": "phoneuser2",
            "email": "phoneuser2@example.com",
            "phone": phone,
            "password": "password123",
        },
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """inactive 用户登录 → 401"""
    from boxbase.zones.admin.models.user import User

    # 注册后通过 DB 将 is_active 设为 False
    register_resp = await client.post(
        "/api/auth/register",
        json={
            "username": "inactiveuser",
            "email": "inactive@example.com",
            "password": "password123",
        },
    )
    assert register_resp.status_code == 201
    user_id = uuid.UUID(register_resp.json()["id"])

    # 直接通过 DB 设为 inactive
    from sqlalchemy import select as sa_select

    result = await db_session.execute(sa_select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    # 用正确密码登录，但 is_active=False
    resp = await client.post(
        "/api/auth/login",
        json={
            "username": "inactiveuser",
            "password": "password123",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_with_explicit_tenant(client: AsyncClient, superadmin_token: str) -> None:
    """登录时显式指定 tenant_id → 200"""
    # 先获取 superadmin 的 tenant 列表
    resp = await client.get(
        "/api/auth/tenants",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert resp.status_code == 200
    tenants = resp.json()
    assert len(tenants) > 0
    tenant_id = tenants[0]["tenant_id"]

    resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["active_tenant_id"] == tenant_id


@pytest.mark.asyncio
async def test_login_invalid_tenant(client: AsyncClient) -> None:
    """登录时指定不存在的 tenant_id → 401"""
    resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
            "tenant_id": str(uuid.uuid4()),
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_missing_jti(client: AsyncClient) -> None:
    """refresh token claims 缺少 jti → 401"""
    import jwt

    from boxbase.core.config import settings

    # 签一个没有 jti 的 refresh token
    bad_token = jwt.encode(
        {"sub": "test", "type": "refresh"},
        settings.secret_key,
        algorithm="HS256",
    )
    resp = await client.post("/api/auth/refresh", json={"refresh_token": bad_token})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_switch_tenant_not_member(client: AsyncClient, superadmin_token: str) -> None:
    """切换到未加入的租户 → 404"""
    resp = await client.post(
        "/api/auth/switch-tenant",
        json={"tenant_id": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_my_tenants_success(client: AsyncClient, superadmin_token: str) -> None:
    """获取我的租户列表 → 200，至少 1 条"""
    resp = await client.get(
        "/api/auth/tenants",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ---------------------------------------------------------------------------
# 补充：refresh rotation 并发宽限窗口测试
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_graceful_concurrent_refresh(client: AsyncClient) -> None:
    """并发 refresh 相同 jti → 宽限窗口内放行，两个都返回 200。

    模拟：两个请求用同一个 refresh_token 几乎同时刷新，
    第一个正常 rotation，第二个因宽限窗口被容错放行。
    """
    # 登录获取 refresh_token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # 第一次 refresh → 200，正常 rotation
    resp1 = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp1.status_code == 200, f"第一次 refresh 应成功: {resp1.text}"
    token1 = resp1.json()
    assert token1["refresh_token"] != refresh_token

    # 第二次用 同一个 jti 再 refresh → 宽限放行，200
    resp2 = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp2.status_code == 200, f"宽限窗口内应放行: {resp2.text}"
    token2 = resp2.json()
    assert token2["refresh_token"] != refresh_token
    # 两次并发产出的是不同的新 jti
    assert token2["refresh_token"] != token1["refresh_token"]


@pytest.mark.asyncio
async def test_logout_revoked_no_grace(client: AsyncClient) -> None:
    """logout revoked 的 jti 不享受宽限 → 401。

    与 rotation-revoke 不同，主动 logout 的 token 必须永远 401。
    """
    # 登录获取 refresh_token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # logout
    logout_resp = await client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_resp.status_code == 204

    # 立即 refresh（logout revoke 不享受宽限）
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 401, f"logout revoke 应返回 401: {resp.text}"
    assert resp.json()["code"] == "AUTH_INVALID_TOKEN"


@pytest.mark.asyncio
async def test_grace_window_expired(client: AsyncClient, monkeypatch) -> None:
    """宽限窗口过期后 rotation-revoked token → 401。

    模拟 revoked_at 超过宽限窗口的旧 jti，确认不放行。
    """
    # 登录获取 refresh_token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # 第一次 refresh → rotation revoke 旧 jti
    resp1 = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp1.status_code == 200

    # 将宽限窗口设为 0，使已 revoke 的 jti 必然过期
    from boxbase.core import config as app_config

    monkeypatch.setattr(app_config.settings, "refresh_rotation_grace_seconds", 0)

    # 第二次用同一个 jti → 401（超过宽限窗口）
    resp2 = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp2.status_code == 401, f"宽限过期应返回 401: {resp2.text}"
    assert resp2.json()["code"] == "AUTH_INVALID_TOKEN"
