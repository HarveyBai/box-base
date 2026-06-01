"""add_revoked_at_and_reason_to_refresh_token

Revision ID: e0757aa877d0
Revises: ed48c00ce20e
Create Date: 2026-06-01 09:33:57.477195
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e0757aa877d0"
down_revision: str | None = "ed48c00ce20e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_token",
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "refresh_token",
        sa.Column("revoked_reason", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("refresh_token", "revoked_reason")
    op.drop_column("refresh_token", "revoked_at")
