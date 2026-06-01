"""BoxBase 数据库引擎与会话工厂。

使用 SQLAlchemy 2.0 async 引擎，SQLite 启用 WAL 日志模式、外键约束、
并全局使用 BEGIN IMMEDIATE 写事务串行化（替代默认 DEFERRED）。
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from boxbase.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)

session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
    """SQLite 连接钩子：启用 WAL 日志模式和外键约束。

    在每个新连接上执行，确保 WAL 模式和外键检查始终生效。

    ⚠️ 副作用需知：
    这里将 dbapi_connection.isolation_level 设为 None，目的是阻止
    SQLAlchemy 的 do_begin 发送默认的 DEFERRED BEGIN。转而由下方的
    "begin" 事件钩子接管，统一发送 BEGIN IMMEDIATE。
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()
    # 关键：关闭 SA 的隐式事务管理，由 begin 事件接管 BEGIN 发送。
    dbapi_connection.isolation_level = None  # noqa: ERA001


def _sqlite_begin_immediate(conn):  # type: ignore[no-untyped-def]
    """SQLite begin 事件钩子：用 BEGIN IMMEDIATE 替代默认 DEFERRED。

    ⚠️ 全局事务行为变更（影响所有 SQLite 写操作，不只是 refresh_token）：
    - BEGIN IMMEDIATE 在事务开始时立即获取 RESERVED 锁，串行化所有写操作。
    - WAL 模式下读操作不受此影响（读取不阻塞、不被阻塞）。
    - PostgreSQL 环境不注册此钩子（PG 使用行级锁 SELECT ... FOR UPDATE）。

    注意：
    - 此钩子在 do_begin（因 isolation_level=None 被跳过）之后触发。
    - 此时尚无事务存在，exec_driver_sql("BEGIN IMMEDIATE") 是安全的。
    - 对单用户开发 / 低并发场景：串行化写开销可忽略。
    - 对高并发场景：所有写被串行化为单队列，需关注吞吐量影响。
    """
    conn.exec_driver_sql("BEGIN IMMEDIATE")


# 仅在 SQLite 驱动下注册上述三个全局钩子，PG 连接不挂任何监听器
if settings.database_url.startswith("sqlite"):
    event.listen(engine.sync_engine, "connect", _set_sqlite_pragma)
    event.listen(engine.sync_engine, "begin", _sqlite_begin_immediate)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供异步数据库会话。

    Yields:
        AsyncSession: 数据库会话，请求结束后自动关闭。
    """
    async with session_factory() as session:
        yield session
