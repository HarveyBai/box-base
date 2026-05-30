"""Role 租户内角色模型。"""

from __future__ import annotations

import uuid

from sqlalchemy import Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class Role(AuditMixin, Base):
    """租户内角色，tenant-scoped。

    name：每租户独立，owner / admin / member 为默认 seed 角色。
    索引：(tenant_id, name) 联合索引。
    """

    __tablename__ = "role"

    __table_args__ = (Index("ix_role_tenant_name", "tenant_id", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
