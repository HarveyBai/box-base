from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.zones.demo.schemas import DemoItemResponse


async def list_items(
    current_tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[DemoItemResponse]:
    """
    示例 service 函数。
    真实模块在此查询自己的业务表，返回数据列表。
    当前 demo 返回空列表，演示结构完整性。
    """
    return []
