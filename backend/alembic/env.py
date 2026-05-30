"""Alembic 迁移环境配置（async 模式）。

复用 boxbase.database 中的 async engine，支持 SQLite 和 PostgreSQL。
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

# 确保 boxbase 包可导入（alembic CLI 运行时不在项目根目录）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alembic import context
from boxbase.config import settings
from boxbase.database import engine
from boxbase.models.base import Base

# Alembic Config 对象，提供 .ini 文件中的值
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 本片无业务表，target_metadata 为 None；切片 2 起改为 Base.metadata
target_metadata = Base.metadata


def do_run_migrations(connection):
    """在同步连接上执行迁移（由 run_sync 调用）。"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """使用 async engine 连接并执行迁移。"""
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_offline():
    """离线模式：生成 SQL 脚本而不连接数据库。

    从 config 获取 URL，若未配置则回退到 settings.database_url。
    """
    url = config.get_main_option("sqlalchemy.url") or settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """在线模式：连接数据库并执行迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
