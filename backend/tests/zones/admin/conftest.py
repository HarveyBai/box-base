"""admin zone 集成测试共享 fixture。

提供：
- 独立内存 SQLite 数据库（带 seed 数据）
- 绑定 db override 的 httpx.AsyncClient
- 测试用户 / 系统租户等引用常量
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import jwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from boxbase.core.base import Base
from boxbase.core.config import settings
from boxbase.core.database import get_db
from boxbase.core.security import hash_password
from boxbase.main import app
from boxbase.zones.admin.models.membership import Membership
from boxbase.zones.admin.models.membership_role import MembershipRole
from boxbase.zones.admin.models.permission import Permission
from boxbase.zones.admin.models.role import Role
from boxbase.zones.admin.models.role_permission import RolePermission
from boxbase.zones.admin.models.tenant import Tenant
from boxbase.zones.admin.models.user import User

# ---------------------------------------------------------------------------
# 测试常量
# ---------------------------------------------------------------------------

SUPERADMIN_USERNAME = "testsuperadmin"
SUPERADMIN_PASSWORD = "testpass123"
SUPERADMIN_EMAIL = "testsuperadmin@example.com"

NORMAL_USERNAME = "testuser"
NORMAL_PASSWORD = "testpass456"
NORMAL_EMAIL = "testuser@example.com"

SYSTEM_TENANT_SLUG = "system"
DEFAULT_ROLES = ["owner", "admin", "member"]
DEFAULT_PERMISSIONS = [
    "user:read",
    "user:write",
    "role:read",
    "role:write",
    "role:assign",
]


# 需要跨 test 访问的数据
class SeedData:
    """存储在内存 DB 中 seed 后的关键 ID。"""

    superadmin_user: User | None = None
    system_tenant: Tenant | None = None
    normal_user: User | None = None
    normal_membership: Membership | None = None
    roles: dict[str, Role] = {}
    permissions: dict[str, Permission] = {}


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


async def _run_seed(db: AsyncSession) -> None:
    """在给定的 db session 中初始化 seed 数据（幂等）。"""
    # 系统租户
    stmt = Tenant.__table__.select().where(Tenant.slug == SYSTEM_TENANT_SLUG)  # type: ignore[attr-defined]
    result = await db.execute(stmt)
    tenant = result.first()
    if tenant is None:
        tenant_id = uuid.uuid4()
        db.add(
            Tenant(
                id=tenant_id,
                slug=SYSTEM_TENANT_SLUG,
                name="BoxBase System",
                is_system=True,
            )
        )
    else:
        tenant_id = uuid.UUID(str(tenant.id))
    await db.flush()

    # 重新获取 tenant 对象
    from sqlalchemy import select as sa_select

    result = await db.execute(sa_select(Tenant).where(Tenant.id == tenant_id))
    tenant_obj = result.scalar_one()
    SeedData.system_tenant = tenant_obj

    # superadmin 用户
    settings.superadmin_username = SUPERADMIN_USERNAME
    result = await db.execute(sa_select(User).where(User.username == SUPERADMIN_USERNAME))
    superadmin = result.scalar_one_or_none()
    if superadmin is None:
        superadmin = User(
            id=uuid.uuid4(),
            username=SUPERADMIN_USERNAME,
            email=SUPERADMIN_EMAIL,
            hashed_password=hash_password(SUPERADMIN_PASSWORD),
            is_active=True,
        )
        db.add(superadmin)
        await db.flush()
    SeedData.superadmin_user = superadmin

    # superadmin membership
    result = await db.execute(
        sa_select(Membership).where(
            Membership.user_id == superadmin.id,
            Membership.tenant_id == tenant_obj.id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        membership = Membership(
            id=uuid.uuid4(),
            tenant_id=tenant_obj.id,
            user_id=superadmin.id,
            is_default=True,
            status="active",
            joined_at=datetime.now(UTC),
        )
        db.add(membership)
        await db.flush()

    # 默认角色
    for name in DEFAULT_ROLES:
        result = await db.execute(
            sa_select(Role).where(
                Role.tenant_id == tenant_obj.id,
                Role.name == name,
            )
        )
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(
                id=uuid.uuid4(),
                tenant_id=tenant_obj.id,
                name=name,
            )
            db.add(role)
            await db.flush()
        SeedData.roles[name] = role

    # 默认权限
    for code in DEFAULT_PERMISSIONS:
        result = await db.execute(
            sa_select(Permission).where(
                Permission.tenant_id == tenant_obj.id,
                Permission.code == code,
            )
        )
        perm = result.scalar_one_or_none()
        if perm is None:
            perm = Permission(
                id=uuid.uuid4(),
                tenant_id=tenant_obj.id,
                code=code,
            )
            db.add(perm)
            await db.flush()
        SeedData.permissions[code] = perm

    # owner 角色绑定全部权限
    owner = SeedData.roles.get("owner")
    if owner:
        for code in DEFAULT_PERMISSIONS:
            perm = SeedData.permissions.get(code)
            if perm is None:
                continue
            result = await db.execute(
                sa_select(RolePermission).where(
                    RolePermission.tenant_id == tenant_obj.id,
                    RolePermission.role_id == owner.id,
                    RolePermission.permission_id == perm.id,
                )
            )
            if result.scalar_one_or_none() is None:
                db.add(
                    RolePermission(
                        id=uuid.uuid4(),
                        tenant_id=tenant_obj.id,
                        role_id=owner.id,
                        permission_id=perm.id,
                    )
                )
        await db.flush()

    # superadmin → owner 角色绑定
    result = await db.execute(
        sa_select(MembershipRole).where(
            MembershipRole.tenant_id == tenant_obj.id,
            MembershipRole.membership_id == membership.id,
            MembershipRole.role_id == owner.id,
        )
    )
    if result.scalar_one_or_none() is None:
        db.add(
            MembershipRole(
                id=uuid.uuid4(),
                tenant_id=tenant_obj.id,
                membership_id=membership.id,
                role_id=owner.id,
            )
        )
        await db.flush()

    # 创建普通测试用户（带 membership + member 角色）
    result = await db.execute(sa_select(User).where(User.username == NORMAL_USERNAME))
    normal_user = result.scalar_one_or_none()
    if normal_user is None:
        normal_user = User(
            id=uuid.uuid4(),
            username=NORMAL_USERNAME,
            email=NORMAL_EMAIL,
            hashed_password=hash_password(NORMAL_PASSWORD),
            is_active=True,
        )
        db.add(normal_user)
        await db.flush()

    SeedData.normal_user = normal_user

    # 普通用户 membership
    result = await db.execute(
        sa_select(Membership).where(
            Membership.user_id == normal_user.id,
            Membership.tenant_id == tenant_obj.id,
        )
    )
    normal_membership = result.scalar_one_or_none()
    if normal_membership is None:
        normal_membership = Membership(
            id=uuid.uuid4(),
            tenant_id=tenant_obj.id,
            user_id=normal_user.id,
            is_default=True,
            status="active",
            joined_at=datetime.now(UTC),
        )
        db.add(normal_membership)
        await db.flush()
    SeedData.normal_membership = normal_membership

    # 普通用户 → member 角色绑定
    member_role = SeedData.roles.get("member")
    if member_role:
        result = await db.execute(
            sa_select(MembershipRole).where(
                MembershipRole.tenant_id == tenant_obj.id,
                MembershipRole.membership_id == normal_membership.id,
                MembershipRole.role_id == member_role.id,
            )
        )
        if result.scalar_one_or_none() is None:
            db.add(
                MembershipRole(
                    id=uuid.uuid4(),
                    tenant_id=tenant_obj.id,
                    membership_id=normal_membership.id,
                    role_id=member_role.id,
                )
            )
            await db.flush()

    await db.commit()


def _make_access_token(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    username: str,
) -> str:
    """签发一个合法的 access token（测试用）。"""
    now = datetime.now(UTC)
    expire = now.replace(year=now.year + 1)
    payload: dict[str, object] = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "usr": username,
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """提供基于内存 SQLite 的隔离 async session，每个测试独立建表 + seed。"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        # 执行 seed
        async with session.begin():
            await _run_seed(session)
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """提供绑定到 FastAPI 应用的异步 HTTP 测试客户端，注入隔离 DB。"""
    app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def superadmin_token() -> str:
    """返回 superadmin 的 access token。"""
    assert SeedData.superadmin_user is not None
    assert SeedData.system_tenant is not None
    return _make_access_token(
        SeedData.superadmin_user.id,
        SeedData.system_tenant.id,
        SUPERADMIN_USERNAME,
    )


@pytest.fixture
def normal_token() -> str:
    """返回普通用户的 access token。"""
    assert SeedData.normal_user is not None
    assert SeedData.system_tenant is not None
    return _make_access_token(
        SeedData.normal_user.id,
        SeedData.system_tenant.id,
        NORMAL_USERNAME,
    )
