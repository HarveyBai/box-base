"""add_successor_jti_to_refresh_token

Revision ID: a1b2c3d4e5f6
Revises: e0757aa877d0
Create Date: 2026-06-01 11:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "e0757aa877d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_token",
        sa.Column("successor_jti", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("refresh_token", "successor_jti")
