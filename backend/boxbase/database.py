"""BoxBase 数据库引擎与会话工厂。

使用 SQLAlchemy 2.0 async 引擎，SQLite 启用 WAL 日志模式和外键约束。
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from boxbase.config import settings

engine = create_async_engine(settings.database_url, echo=False)

session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
    """SQLite 连接钩子：启用 WAL 日志模式和外键约束。

    在每个新连接上执行，确保 WAL 模式和外键检查始终生效。
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


# 仅在 SQLite 驱动下注册 WAL/外键注入，PG 连接不挂此监听器
if settings.database_url.startswith("sqlite"):
    event.listen(engine.sync_engine, "connect", _set_sqlite_pragma)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供异步数据库会话。

    Yields:
        AsyncSession: 数据库会话，请求结束后自动关闭。
    """
    async with session_factory() as session:
        yield session
