from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str


class ErrorCode:
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_INACTIVE_USER = "AUTH_INACTIVE_USER"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    TENANT_NOT_FOUND = "TENANT_NOT_FOUND"
    MEMBERSHIP_NOT_FOUND = "MEMBERSHIP_NOT_FOUND"
    MEMBERSHIP_ALREADY_EXISTS = "MEMBERSHIP_ALREADY_EXISTS"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    ROLE_NOT_FOUND = "ROLE_NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """将 HTTPException 统一转为 ErrorResponse 格式输出"""
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        content = exc.detail
    else:
        content = ErrorResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message=str(exc.detail) if exc.detail else "An error occurred",
        ).model_dump()
    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """将 Pydantic 422 校验错误统一转为 ErrorResponse 格式输出"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message=str(exc.errors()),
        ).model_dump(),
    )
