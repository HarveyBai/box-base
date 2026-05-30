"""BoxBase FastAPI 依赖注入基础设施。

RequestContext：请求生命周期内的身份上下文，
               由 get_current_user（切片 7）构造并通过 Depends 传递。
apply_soft_delete_filter：为查询语句注入 deleted_at IS NULL 过滤。
apply_tenant_filter：为查询语句注入 tenant_id = active_tenant_id 过滤。
require_active_membership：校验当前用户在活跃租户有 active membership（切片 7 补全）。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sqlalchemy import Select, and_

if TYPE_CHECKING:
    pass


@dataclass
class RequestContext:
    """请求生命周期内的身份上下文。

    由 get_current_user 依赖（切片 7）构造，通过 FastAPI Depends 传递给下游依赖和路由。

    Attributes:
        user_id: 当前登录用户的全局 UUID。
        active_tenant_id: token 中携带的活跃租户 UUID。
        is_superadmin: 是否为超级管理员（配置文件注入，short-circuit 绕过 RBAC）。
    """

    user_id: uuid.UUID
    active_tenant_id: uuid.UUID
    is_superadmin: bool = field(default=False)


def apply_soft_delete_filter(stmt: Select[Any], model: Any) -> Select[Any]:
    """为查询语句注入软删除过滤条件（deleted_at IS NULL）。

    Args:
        stmt: 原始 SQLAlchemy select 语句。
        model: 带有 deleted_at 字段的 ORM 模型类。

    Returns:
        追加了 deleted_at IS NULL 条件的新语句。

    Example:
        stmt = apply_soft_delete_filter(select(User), User)
    """
    return stmt.where(model.deleted_at.is_(None))


def apply_tenant_filter(
    stmt: Select[Any],
    model: Any,
    tenant_id: uuid.UUID,
) -> Select[Any]:
    """为查询语句注入租户隔离过滤条件（tenant_id = :tenant_id AND deleted_at IS NULL）。

    同时注入软删除过滤，确保租户隔离与软删除两层条件同时生效。

    Args:
        stmt: 原始 SQLAlchemy select 语句。
        model: 带有 tenant_id 和 deleted_at 字段的 ORM 模型类。
        tenant_id: 当前活跃租户 UUID，来自 RequestContext.active_tenant_id。

    Returns:
        追加了 tenant_id 与 deleted_at 双重过滤条件的新语句。

    Example:
        stmt = apply_tenant_filter(select(Role), Role, ctx.active_tenant_id)
    """
    return stmt.where(
        and_(
            model.tenant_id == tenant_id,
            model.deleted_at.is_(None),
        )
    )


async def require_active_membership(
    # ctx: RequestContext  ← 切片 7 接入 get_current_user 后解注释并补全实现
) -> None:
    """校验当前用户在活跃租户有 active membership。

    切片 7 实现：从 RequestContext 取 user_id + active_tenant_id，
    查询 Membership 表确认 status='active' 且 deleted_at IS NULL，
    不满足则抛出 403。

    当前为占位实现，切片 7 补全。
    """
