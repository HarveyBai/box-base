"""BoxBase FastAPI 应用入口。"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from boxbase import __version__
from boxbase.core.exceptions import http_exception_handler, validation_exception_handler
from boxbase.core.router import api_router

app = FastAPI(
    title="BoxBase API",
    description="轻量级模块化 Python 多租户 SaaS 框架",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]

app.include_router(api_router, prefix="/api")
