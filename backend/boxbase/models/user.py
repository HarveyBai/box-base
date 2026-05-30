"""User 全局实体模型。"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class User(AuditMixin, Base):
    """全局用户，不属于任何租户，经 Membership 加入多租户。

    唯一约束：
    - username：全局唯一
    - email：全局唯一
    - phone：全局唯一索引，允许多 NULL（SQLite / PG 均支持）
    """

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
