"""Tenant 多租户实体模型。"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class Tenant(AuditMixin, Base):
    """租户实体。

    slug：全局唯一索引，子域名/友好 URL 预留，v1.0 不强依赖路由。
    is_system：True 的那条同时是内置默认租户与超管系统保留租户（唯一一条）。
    """

    __tablename__ = "tenant"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
