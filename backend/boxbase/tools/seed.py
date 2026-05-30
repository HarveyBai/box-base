"""BoxBase 数据库初始化 seed 脚本。

幂等执行：重复运行不会产生重复数据。
用法：cd backend && uv run python -m boxbase.tools.seed

Seed 内容：
1. 系统租户（slug=system，is_system=True）——内置默认租户 + 超管保留租户合并为一条
2. superadmin 用户（username 来自 config.superadmin_username，跳过若未配置）
3. superadmin 加入系统租户 membership（is_default=True，status=active）
4. 系统租户默认角色（owner / admin / member）
5. 系统租户默认权限集（user:read / user:write / role:read / role:write / role:assign）
6. owner 角色绑定全部权限
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.config import settings
from boxbase.database import session_factory
from boxbase.models.membership import Membership
from boxbase.models.membership_role import MembershipRole
from boxbase.models.permission import Permission
from boxbase.models.role import Role
from boxbase.models.role_permission import RolePermission
from boxbase.models.tenant import Tenant
from boxbase.models.user import User
from boxbase.security import hash_password

# --------------------------------------------------------------------------- #
# 常量
# --------------------------------------------------------------------------- #

SYSTEM_TENANT_SLUG = "system"
SYSTEM_TENANT_NAME = "BoxBase System"

DEFAULT_ROLES = ["owner", "admin", "member"]

DEFAULT_PERMISSIONS = [
    "user:read",
    "user:write",
    "role:read",
    "role:write",
    "role:assign",
]

# owner 角色拥有全部权限
OWNER_PERMISSIONS = DEFAULT_PERMISSIONS


# --------------------------------------------------------------------------- #
# 辅助函数
# --------------------------------------------------------------------------- #


def _now() -> datetime:
    return datetime.now(UTC)


async def _get_or_create_tenant(db: AsyncSession) -> Tenant:
    """获取或创建系统租户（幂等）。"""
    stmt = select(Tenant).where(Tenant.slug == SYSTEM_TENANT_SLUG)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(
            id=uuid.uuid4(),
            slug=SYSTEM_TENANT_SLUG,
            name=SYSTEM_TENANT_NAME,
            is_system=True,
        )
        db.add(tenant)
        await db.flush()
        print(f"  [+] 系统租户已创建：{SYSTEM_TENANT_SLUG}")
    else:
        print(f"  [=] 系统租户已存在：{SYSTEM_TENANT_SLUG}")
    return tenant


async def _get_or_create_superadmin(db: AsyncSession) -> User | None:
    """获取或创建 superadmin 用户（幂等）。跳过若 superadmin_username 未配置。"""
    username = settings.superadmin_username
    if not username:
        print("  [!] superadmin_username 未配置，跳过 superadmin seed")
        return None

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        # 默认密码：superadmin，生产环境必须通过 .env 覆盖
        default_password = "superadmin-change-me"
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=f"{username}@system.local",
            hashed_password=hash_password(default_password),
            is_active=True,
        )
        db.add(user)
        await db.flush()
        print(f"  [+] superadmin 用户已创建：{username}（默认密码：{default_password}）")
    else:
        print(f"  [=] superadmin 用户已存在：{username}")
    return user


async def _get_or_create_membership(
    db: AsyncSession,
    user: User,
    tenant: Tenant,
) -> Membership:
    """获取或创建 superadmin 的系统租户 membership（幂等）。"""
    stmt = select(Membership).where(
        Membership.user_id == user.id,
        Membership.tenant_id == tenant.id,
    )
    result = await db.execute(stmt)
    membership = result.scalar_one_or_none()
    if membership is None:
        membership = Membership(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            user_id=user.id,
            is_default=True,
            status="active",
            joined_at=_now(),
        )
        db.add(membership)
        await db.flush()
        print(f"  [+] superadmin membership 已创建（tenant={tenant.slug}）")
    else:
        print(f"  [=] superadmin membership 已存在（tenant={tenant.slug}）")
    return membership


async def _seed_roles(db: AsyncSession, tenant: Tenant) -> dict[str, Role]:
    """为租户 seed 默认角色（幂等），返回 name→Role 映射。"""
    roles: dict[str, Role] = {}
    for name in DEFAULT_ROLES:
        stmt = select(Role).where(
            Role.tenant_id == tenant.id,
            Role.name == name,
        )
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name=name,
            )
            db.add(role)
            await db.flush()
            print(f"  [+] 角色已创建：{name}")
        else:
            print(f"  [=] 角色已存在：{name}")
        roles[name] = role
    return roles


async def _seed_permissions(db: AsyncSession, tenant: Tenant) -> dict[str, Permission]:
    """为租户 seed 默认权限集（幂等），返回 code→Permission 映射。"""
    permissions: dict[str, Permission] = {}
    for code in DEFAULT_PERMISSIONS:
        stmt = select(Permission).where(
            Permission.tenant_id == tenant.id,
            Permission.code == code,
        )
        result = await db.execute(stmt)
        perm = result.scalar_one_or_none()
        if perm is None:
            perm = Permission(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                code=code,
            )
            db.add(perm)
            await db.flush()
            print(f"  [+] 权限已创建：{code}")
        else:
            print(f"  [=] 权限已存在：{code}")
        permissions[code] = perm
    return permissions


async def _seed_owner_permissions(
    db: AsyncSession,
    tenant: Tenant,
    roles: dict[str, Role],
    permissions: dict[str, Permission],
) -> None:
    """为 owner 角色绑定全部权限（幂等）。"""
    owner = roles.get("owner")
    if owner is None:
        return
    for code in OWNER_PERMISSIONS:
        perm = permissions.get(code)
        if perm is None:
            continue
        stmt = select(RolePermission).where(
            RolePermission.tenant_id == tenant.id,
            RolePermission.role_id == owner.id,
            RolePermission.permission_id == perm.id,
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            rp = RolePermission(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                role_id=owner.id,
                permission_id=perm.id,
            )
            db.add(rp)
            print(f"  [+] owner 权限绑定：{code}")
        else:
            print(f"  [=] owner 权限已绑定：{code}")
    await db.flush()


async def _seed_superadmin_role(
    db: AsyncSession,
    tenant: Tenant,
    membership: Membership,
    roles: dict[str, Role],
) -> None:
    """为 superadmin membership 绑定 owner 角色（幂等）。"""
    owner = roles.get("owner")
    if owner is None:
        return
    stmt = select(MembershipRole).where(
        MembershipRole.tenant_id == tenant.id,
        MembershipRole.membership_id == membership.id,
        MembershipRole.role_id == owner.id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is None:
        mr = MembershipRole(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            membership_id=membership.id,
            role_id=owner.id,
        )
        db.add(mr)
        await db.flush()
        print("  [+] superadmin → owner 角色已绑定")
    else:
        print("  [=] superadmin → owner 角色已存在")


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #


async def run_seed() -> None:
    """执行完整 seed 流程。"""
    print("=== BoxBase Seed 开始 ===")

    async with session_factory() as db:
        async with db.begin():
            print("[1] 系统租户")
            tenant = await _get_or_create_tenant(db)

            print("[2] superadmin 用户")
            superadmin = await _get_or_create_superadmin(db)

            if superadmin is not None:
                print("[3] superadmin membership")
                membership = await _get_or_create_membership(db, superadmin, tenant)

            print("[4] 默认角色")
            roles = await _seed_roles(db, tenant)

            print("[5] 默认权限集")
            permissions = await _seed_permissions(db, tenant)

            print("[6] owner 权限绑定")
            await _seed_owner_permissions(db, tenant, roles, permissions)

            if superadmin is not None:
                print("[7] superadmin → owner 角色绑定")
                await _seed_superadmin_role(db, tenant, membership, roles)

    print("=== BoxBase Seed 完成 ===")


if __name__ == "__main__":
    asyncio.run(run_seed())
