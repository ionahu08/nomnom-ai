"""Add health profile fields: race, goal, medical_conditions, surgeries, medications."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260613_add_health_profile_fields"
down_revision = "f2c3a8d9e1f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to user_profiles table
    op.add_column("user_profiles", sa.Column("race", sa.String(50), nullable=True))
    op.add_column(
        "user_profiles",
        sa.Column(
            "goal",
            sa.String(20),
            nullable=True,
            comment="Fitness goal: lose_weight, maintain, gain_muscle, shape_figure",
        ),
    )
    op.add_column(
        "user_profiles",
        sa.Column("medical_conditions", postgresql.JSON(), nullable=True, default=[]),
    )
    op.add_column(
        "user_profiles", sa.Column("surgeries", postgresql.JSON(), nullable=True, default=[])
    )
    op.add_column(
        "user_profiles",
        sa.Column("medications", postgresql.JSON(), nullable=True, default=[]),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "medications")
    op.drop_column("user_profiles", "surgeries")
    op.drop_column("user_profiles", "medical_conditions")
    op.drop_column("user_profiles", "goal")
    op.drop_column("user_profiles", "race")
