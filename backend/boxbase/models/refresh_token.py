"""RefreshToken 会话令牌模型。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from boxbase.models.base import AuditMixin, Base


class RefreshToken(AuditMixin, Base):
    """Refresh Token 白名单存储，支持 rotation 与强制下线。

    jti：JWT ID，明文 UUID 字符串，唯一索引，rotation 时旧 jti→revoked。
    status：active / revoked。
    tenant_id：签发时的活跃租户，row-level 隔离。
    expires_at：过期时间戳，索引用于清理过期记录。
    索引：jti 唯一索引、(tenant_id, user_id) 联合索引、expires_at 索引。
    """

    __tablename__ = "refresh_token"

    __table_args__ = (
        Index("ix_refresh_token_jti", "jti", unique=True),
        Index("ix_refresh_token_tenant_user", "tenant_id", "user_id"),
        Index("ix_refresh_token_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    jti: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
