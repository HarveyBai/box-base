"""baseline

Revision ID: b845e3107bf8
Revises:
Create Date: 2026-05-30 22:21:14.184565
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "b845e3107bf8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
