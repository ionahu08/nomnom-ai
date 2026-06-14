"""remove race field

Revision ID: e8b5e39cfa42
Revises: d76db7f96f20
Create Date: 2026-06-14 14:50:17.715319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8b5e39cfa42'
down_revision: Union[str, None] = 'd76db7f96f20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user_profiles", "race")


def downgrade() -> None:
    op.add_column("user_profiles", sa.Column("race", sa.String(50), nullable=True))
