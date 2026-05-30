"""RolePermission 关联表：role ↔ permission。"""

from __future__ import annotations

import uuid

from sqlalchemy import Index, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class RolePermission(AuditMixin, Base):
    """Role 与 Permission 的多对多关联，tenant-scoped。

    唯一约束：(tenant_id, role_id, permission_id)。
    """

    __tablename__ = "role_permission"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "role_id",
            "permission_id",
            name="uq_role_permission",
        ),
        Index("ix_role_permission_role_id", "role_id"),
        Index("ix_role_permission_permission_id", "permission_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    permission_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
