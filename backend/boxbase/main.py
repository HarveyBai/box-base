"""BoxBase FastAPI 应用入口。"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from boxbase import __version__


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


# 创建 FastAPI 应用实例，版本号从包元信息读取
app = FastAPI(
    title="BoxBase API",
    description="轻量级模块化 Python 多租户 SaaS 框架",
    version=__version__,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """健康检查端点，返回服务元信息。

    返回：
        HealthResponse: 包含 status="ok"、当前版本号和服务标识的固定响应。
    """
    # 直接返回固定响应，version 从 __version__ 读取保证与包元信息一致
    return HealthResponse(status="ok", version=__version__, service="boxbase")
