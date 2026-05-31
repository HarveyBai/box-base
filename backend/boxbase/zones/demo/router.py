from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from boxbase.core.dependencies import RequestContext, get_db
from boxbase.core.security import get_current_user
from boxbase.zones.demo import service
from boxbase.zones.demo.schemas import DemoItemResponse

router = APIRouter()


@router.get("/demo/items", response_model=list[DemoItemResponse], tags=["Demo"])
async def list_items(
    ctx: RequestContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DemoItemResponse]:
    """
    Demo 模块示例端点。
    扩展模块开发参考：
    1. 在 zones/<module>/models/ 定义业务表（继承 AuditMixin，带 tenant_id）
    2. 在 zones/<module>/schemas.py 定义 request/response schema
    3. 在 zones/<module>/service.py 实现业务逻辑
    4. 在 zones/<module>/router.py 定义端点（薄 router，调用 service）
    5. 在 core/router.py 追加一行 include 新模块 router
    """
    return await service.list_items(ctx.active_tenant_id, db)
