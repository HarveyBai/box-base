"""OpenAPI 文档端点的测试套件。

验证 /openapi.json、/docs、/redoc 三个端点均可正常访问。
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
async def test_openapi_json_returns_200(client: AsyncClient) -> None:
    """验证 GET /openapi.json 返回 200 且响应体为合法的 OpenAPI JSON。

    参数：
        client: 异步 HTTP 测试客户端 fixture。
    """
    response = await client.get("/openapi.json")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    body = response.json()
    assert "openapi" in body, "OpenAPI JSON missing 'openapi' key"
    assert body["info"]["title"] == "BoxBase API"
    assert body["info"]["version"] is not None


@pytest.mark.asyncio
async def test_docs_swagger_ui_returns_200(client: AsyncClient) -> None:
    """验证 GET /docs（Swagger UI）返回 200。

    参数：
        client: 异步 HTTP 测试客户端 fixture。
    """
    response = await client.get("/docs")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


@pytest.mark.asyncio
async def test_redoc_returns_200(client: AsyncClient) -> None:
    """验证 GET /redoc（ReDoc）返回 200。

    参数：
        client: 异步 HTTP 测试客户端 fixture。
    """
    response = await client.get("/redoc")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
