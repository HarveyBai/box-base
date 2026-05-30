"""ORM 声明基类与审计 Mixin。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class AuditMixin:
    """统一审计字段，所有业务表继承。

    - created_at / updated_at：UTC 时间戳，自动维护
    - created_by / updated_by：操作用户 UUID，nullable（seed 场景可空）
    - deleted_at：软删除时间戳，null = 未删；ORM 过滤逻辑切片 6 统一注入
    """

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
