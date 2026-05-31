"""BoxBase 平台路由总入口。"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from boxbase import __version__

api_router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模型。

    属性：
        status: 服务健康时固定为 "ok"。
        version: 当前 BoxBase 包的版本号。
        service: 固定为 "boxbase"，标识本服务。
    """

    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]
    version: str
    service: Literal["boxbase"]


@api_router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """健康检查端点，返回服务元信息。

    返回：
        HealthResponse: 包含 status="ok"、当前版本号和服务标识的固定响应。
    """
    return HealthResponse(status="ok", version=__version__, service="boxbase")
