"""MembershipRole 关联表：membership ↔ role。"""

from __future__ import annotations

import uuid

from sqlalchemy import Index, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class MembershipRole(AuditMixin, Base):
    """Membership 与 Role 的多对多关联，tenant-scoped。

    唯一约束：(tenant_id, membership_id, role_id)。
    """

    __tablename__ = "membership_role"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "membership_id",
            "role_id",
            name="uq_membership_role",
        ),
        Index("ix_membership_role_membership_id", "membership_id"),
        Index("ix_membership_role_role_id", "role_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    membership_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
