"""create nutrition_chat_messages table

Revision ID: f9c8d2e3a5b1
Revises: e8b5e39cfa42
Create Date: 2026-06-15 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9c8d2e3a5b1'
down_revision: Union[str, None] = 'e8b5e39cfa42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'nutrition_chat_messages',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_created', 'nutrition_chat_messages', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_user_created', table_name='nutrition_chat_messages')
    op.drop_table('nutrition_chat_messages')
