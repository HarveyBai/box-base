"""Permission 租户内权限模型。"""

from __future__ import annotations

import uuid

from sqlalchemy import Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class Permission(AuditMixin, Base):
    """租户内权限，tenant-scoped，随租户 seed 固定集。

    code：权限串格式为 resource:action，如 user:read / role:write。
    索引：(tenant_id, code) 联合索引。
    """

    __tablename__ = "permission"

    __table_args__ = (Index("ix_permission_tenant_code", "tenant_id", "code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
