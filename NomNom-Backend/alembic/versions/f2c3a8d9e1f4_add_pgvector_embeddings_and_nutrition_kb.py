"""add pgvector embeddings and nutrition_kb

Revision ID: f2c3a8d9e1f4
Revises: eface4bf2d85
Create Date: 2026-04-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "f2c3a8d9e1f4"
down_revision: Union[str, None] = "eface4bf2d85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding column to food_logs
    op.add_column("food_logs", sa.Column("embedding", Vector(384), nullable=True))

    # Create nutrition_kb table
    op.create_table(
        "nutrition_kb",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # HNSW index on nutrition_kb.embedding for fast ANN search
    op.execute(
        """
        CREATE INDEX nutrition_kb_embedding_idx
        ON nutrition_kb
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    # Drop HNSW index
    op.execute("DROP INDEX IF EXISTS nutrition_kb_embedding_idx")

    # Drop nutrition_kb table
    op.drop_table("nutrition_kb")

    # Drop embedding column from food_logs
    op.drop_column("food_logs", "embedding")

    # Note: Do NOT drop vector extension — other tables or users may rely on it
