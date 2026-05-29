"""/api/health 端点的测试套件。

AC ID: AC0.1-health-endpoint
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from boxbase.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """提供绑定到 FastAPI 应用的异步 HTTP 测试客户端。

    返回：
        AsyncClient: 通过 ASGI transport 配置的 httpx 异步客户端。
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_returns_expected_response(client: AsyncClient) -> None:
    """验证 GET /api/health 返回正确的 status、version 和 service 字段。

    参数：
        client: 异步 HTTP 测试客户端 fixture。

    异常：
        AssertionError: 当状态码、响应体或任意字段不符合预期契约时抛出。
    """
    response = await client.get("/api/health")

    # 断言 HTTP 状态码为 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    body = response.json()

    # 断言 status 字段
    assert body["status"] == "ok", f"Expected status='ok', got {body['status']!r}"

    # 断言 version 字段存在且非空
    assert "version" in body, "Response missing 'version' field"
    assert isinstance(body["version"], str), "Version must be a string"
    assert len(body["version"]) > 0, "Version must not be empty"

    # 断言 service 字段
    assert body["service"] == "boxbase", f"Expected service='boxbase', got {body['service']!r}"
