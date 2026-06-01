"""BoxBase 应用配置模块。"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./boxbase.db"

    # JWT
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 超级管理员（配置文件注入，short-circuit 绕过 RBAC）
    superadmin_username: str = ""

    # refresh rotation 并发宽限窗口（秒）
    # 当同一 jti 被 rotation 后极短时间内再次被用来刷新时，
    # 若 revoke 原因是 "rotation" 且在窗口内，则并发容错放行而非 401。
    refresh_rotation_grace_seconds: int = 10


settings = Settings()
