"""BoxBase FastAPI 依赖注入基础设施。"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.database import get_db
from boxbase.models.membership import Membership


@dataclass
class RequestContext:
    """请求生命周期内的身份上下文。"""

    user_id: uuid.UUID
    active_tenant_id: uuid.UUID
    is_superadmin: bool = field(default=False)


def apply_soft_delete_filter(stmt: Select[Any], model: Any) -> Select[Any]:
    """为查询语句注入软删除过滤条件（deleted_at IS NULL）。"""
    return stmt.where(model.deleted_at.is_(None))


def apply_tenant_filter(
    stmt: Select[Any],
    model: Any,
    tenant_id: uuid.UUID,
) -> Select[Any]:
    """为查询语句注入租户隔离过滤条件（tenant_id + deleted_at IS NULL）。"""
    return stmt.where(
        and_(
            model.tenant_id == tenant_id,
            model.deleted_at.is_(None),
        )
    )


async def require_active_membership(
    ctx: Annotated[RequestContext, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """校验当前用户在活跃租户有 active membership。

    超管 short-circuit：is_superadmin=True 时直接放行。

    Raises:
        HTTPException 403：无 active membership
    """
    if ctx.is_superadmin:
        return

    stmt = select(Membership).where(
        Membership.user_id == ctx.user_id,
        Membership.tenant_id == ctx.active_tenant_id,
        Membership.status == "active",
        Membership.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active membership in the specified tenant",
        )
