"""BoxBase 应用配置模块。

通过 pydantic-settings 从环境变量和 .env 文件加载配置。
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，支持环境变量和 .env 文件覆盖。

    Attributes:
        database_url: 数据库连接 URL，默认使用 SQLite async 驱动。
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./boxbase.db"


settings = Settings()
