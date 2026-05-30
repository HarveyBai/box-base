"""Membership 多租户成员关联模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class Membership(AuditMixin, Base):
    """用户与租户的多对多关联，租户内身份载体。

    唯一约束：(tenant_id, user_id) 数据库级强制，一个用户在同一租户只能有一条记录。
    is_default：标记该用户的默认租户（登录未指定时进入）；
               每用户至多一条 active 的约束由 service 层保证（切片 8）。
    status：active / invited / disabled。
    """

    __tablename__ = "membership"

    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),
        Index("ix_membership_user_id", "user_id"),
        Index("ix_membership_user_default", "user_id", "is_default"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
