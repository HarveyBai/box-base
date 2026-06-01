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
    第一个正常 rotation（Branch A → INSERT 新行），
    第二个因宽限窗口走纯读路径（Branch B → 读取 successor_jti 重签）。

    两个请求拿到的 token jti 应该相同（都是 successor_jti）。
    """
    from boxbase.core.security import decode_refresh_token

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

    # 第一次 refresh → 200，正常 rotation（Branch A — 唯一插入）
    resp1 = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp1.status_code == 200, f"第一次 refresh 应成功: {resp1.text}"
    token1 = resp1.json()
    assert token1["refresh_token"] != refresh_token

    # 第二次用 同一个 jti 再 refresh → 宽限放行（Branch B — 纯读）
    resp2 = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp2.status_code == 200, f"宽限窗口内应放行: {resp2.text}"
    token2 = resp2.json()
    assert token2["refresh_token"] != refresh_token

    # 两次并发产出相同的 successor_jti（Branch B 只读不改指针）
    jti_a = decode_refresh_token(token1["refresh_token"])["jti"]
    jti_b = decode_refresh_token(token2["refresh_token"])["jti"]
    assert jti_b == jti_a, f"Branch B 应返回与 Branch A 相同的 successor_jti，但得到: A={jti_a} B={jti_b}"


@pytest.mark.asyncio
async def test_rotation_branch_b_deterministic(client: AsyncClient, db_session: AsyncSession) -> None:
    """确定性测试 Branch B 纯读路径：无孤儿 active 行。

    方案：先 commit 第一个 rotation 制造 revoked+successor_jti 状态，
    再用旧 jti 发第二个 refresh，确认走 Branch B 纯读路径返回 successor_jti、
    且不新增 active 行（active count = 1，不是 2）。

    此测试是「真正能验证 Branch B 不插入」的底线覆盖。
    """

    from sqlalchemy import select as sa_select

    from boxbase.core.security import decode_refresh_token
    from boxbase.zones.admin.models.refresh_token import RefreshToken

    assert SeedData.superadmin_user is not None
    assert SeedData.system_tenant is not None

    user_id = SeedData.superadmin_user.id

    # Step 1：通过登录获取一个真实的 refresh_token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    old_refresh_token = login_resp.json()["refresh_token"]
    old_claims = decode_refresh_token(old_refresh_token)
    old_jti = old_claims["jti"]

    # Step 2：第一次 refresh（Branch A → rotation），拿到 successor
    resp_a = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert resp_a.status_code == 200, f"Branch A failed: {resp_a.text}"
    token_a = resp_a.json()
    successor_refresh = token_a["refresh_token"]
    successor_claims = decode_refresh_token(successor_refresh)
    successor_jti = successor_claims["jti"]

    # 验证 DB 中旧行有 successor_jti 指针
    result = await db_session.execute(sa_select(RefreshToken).where(RefreshToken.jti == old_jti))
    old_row = result.scalar_one()
    assert old_row.status == "revoked", f"旧行应为 revoked，实际: {old_row.status}"
    assert old_row.revoked_reason == "rotation", "revoke 原因应为 rotation"
    assert old_row.successor_jti == successor_jti, (
        f"旧行 successor_jti 应指向 {successor_jti}，实际: {old_row.successor_jti}"
    )

    # 记录当前该用户 active 行数
    active_stmt = sa_select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.status == "active",
        RefreshToken.deleted_at.is_(None),
    )
    result = await db_session.execute(active_stmt)
    active_before = len(result.scalars().all())

    # Step 3：用 OLD jti 发第二个 refresh（Branch B — 纯读路径）
    resp_b = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert resp_b.status_code == 200, f"Branch B failed: {resp_b.text}"
    token_b = resp_b.json()
    claims_b = decode_refresh_token(token_b["refresh_token"])
    jti_b = claims_b["jti"]

    # Branch B 必须返回与 successor_jti 相同的 jti
    assert jti_b == successor_jti, f"Branch B jti 应等于 successor_jti {successor_jti}，但得到 {jti_b}"

    # Branch B 不应插入新行：active 行数不变
    result = await db_session.execute(active_stmt)
    active_after = len(result.scalars().all())
    assert active_after == active_before, f"Branch B 不应新增 active 行: before={active_before}, after={active_after}"

    # 该用户总共只有 1 个 active 行（不是 2 个）
    assert active_after == 1, f"该用户应有且仅有 1 个 active refresh token 行，实际: {active_after}"


@pytest.mark.asyncio
async def test_switch_tenant_no_successor_returns_401(client: AsyncClient, db_session: AsyncSession) -> None:
    """模拟 switch_tenant 场景：revoked_reason="rotation" 但无 successor_jti → Branch B 应 401。

    switch_tenant 不做 successor 指针，旧 jti 在宽限内也应被拒绝。
    通过 DB 模拟 revoked（reason="rotation"，successor_jti=NULL），
    验证 Branch B 的纯读路径在无 successor_jti 时正确返回 401。
    """
    from datetime import UTC, datetime

    from sqlalchemy import select as sa_select

    from boxbase.core.security import decode_refresh_token
    from boxbase.zones.admin.models.refresh_token import RefreshToken

    assert SeedData.superadmin_user is not None
    assert SeedData.system_tenant is not None

    # 登录获取 refresh_token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD,
        },
    )
    assert login_resp.status_code == 200
    old_refresh_token = login_resp.json()["refresh_token"]
    old_claims = decode_refresh_token(old_refresh_token)
    old_jti = old_claims["jti"]

    # 通过 DB 直接 revoke 该 token（模拟 switch_tenant：无 successor_jti）
    result = await db_session.execute(sa_select(RefreshToken).where(RefreshToken.jti == old_jti))
    old_row = result.scalar_one()
    old_row.status = "revoked"
    old_row.revoked_at = datetime.now(UTC)
    old_row.revoked_reason = "rotation"
    old_row.successor_jti = None  # 关键：无指针
    await db_session.commit()

    # 在宽限窗口内用旧 jti refresh → 应 401（无 successor 放行）
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert resp.status_code == 401, f"无 successor_jti 时即使宽限也应为 401，实际: {resp.status_code}"
    assert resp.json()["code"] == "AUTH_INVALID_TOKEN"


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


# ---------------------------------------------------------------------------
# 过期 token 清理
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cleanup_expired_deletes_only_expired(client: AsyncClient, db_session: AsyncSession) -> None:
    """清理函数只删过期 token，不动未过期的 active token。"""
    from datetime import UTC, datetime, timedelta

    from tests.zones.admin.conftest import SeedData

    assert SeedData.system_tenant is not None
    assert SeedData.superadmin_user is not None

    from boxbase.zones.admin.models.refresh_token import RefreshToken
    from boxbase.zones.admin.services.auth import cleanup_expired_refresh_tokens

    now = datetime.now(UTC)
    expired_jti = str(uuid.uuid4())
    active_jti = str(uuid.uuid4())

    expired = RefreshToken(
        tenant_id=SeedData.system_tenant.id,
        user_id=SeedData.superadmin_user.id,
        jti=expired_jti,
        status="active",
        expires_at=now - timedelta(hours=1),
    )
    active = RefreshToken(
        tenant_id=SeedData.system_tenant.id,
        user_id=SeedData.superadmin_user.id,
        jti=active_jti,
        status="active",
        expires_at=now + timedelta(days=30),
    )
    db_session.add(expired)
    db_session.add(active)
    await db_session.commit()

    # 执行清理
    deleted = await cleanup_expired_refresh_tokens(db_session)
    assert deleted == 1, f"Expected 1 deleted, got {deleted}"

    # 验证：过期 token 已删除，未过期 token 仍存在
    from sqlalchemy import select as sa_select

    result = await db_session.execute(sa_select(RefreshToken).where(RefreshToken.jti == expired_jti))
    assert result.scalar_one_or_none() is None, "Expired token should be deleted"

    result = await db_session.execute(sa_select(RefreshToken).where(RefreshToken.jti == active_jti))
    assert result.scalar_one_or_none() is not None, "Active token should remain"


@pytest.mark.asyncio
async def test_cleanup_no_expired_returns_zero(client: AsyncClient, db_session: AsyncSession) -> None:
    """没有过期 token 时返回 0，不影响任何记录。"""
    from sqlalchemy import select as sa_select

    from boxbase.zones.admin.models.refresh_token import RefreshToken
    from boxbase.zones.admin.services.auth import cleanup_expired_refresh_tokens

    deleted = await cleanup_expired_refresh_tokens(db_session)
    assert deleted >= 0
    # 所有正常 token（如 seed 产生的登录 token）都不应被删
    result = await db_session.execute(sa_select(RefreshToken).where(RefreshToken.deleted_at.is_(None)))
    count_before = len(result.scalars().all())

    deleted = await cleanup_expired_refresh_tokens(db_session)
    result = await db_session.execute(sa_select(RefreshToken).where(RefreshToken.deleted_at.is_(None)))
    count_after = len(result.scalars().all())

    assert count_before == count_after, f"No tokens should be deleted: {count_before} vs {count_after}"
    assert deleted == 0


# ---------------------------------------------------------------------------
# 清理端点集成测试
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cleanup_endpoint_superadmin_success(client: AsyncClient, superadmin_token: str) -> None:
    """超管调用清理端点 → 200，返回 deleted count。"""
    resp = await client.post(
        "/api/admin/maintenance/cleanup-refresh-tokens",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "deleted" in body
    assert isinstance(body["deleted"], int)
    assert body["deleted"] >= 0


@pytest.mark.asyncio
async def test_cleanup_endpoint_normal_user_forbidden(client: AsyncClient, normal_token: str) -> None:
    """普通用户调用清理端点 → 403。"""
    resp = await client.post(
        "/api/admin/maintenance/cleanup-refresh-tokens",
        headers={"Authorization": f"Bearer {normal_token}"},
    )
    assert resp.status_code == 403, resp.text
    body = resp.json()
    assert body["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_grace_window_expired(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
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
