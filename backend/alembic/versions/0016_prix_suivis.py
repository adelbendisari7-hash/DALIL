"""Prix suivis : alerte de baisse de prix d'une pièce.

Revision ID: 0016
Revises: 0015
"""
from alembic import op
import sqlalchemy as sa

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_watches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("part_categories.id"), nullable=False),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("vehicle_variants.id"), nullable=True),
        sa.Column("reference_price", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", name="uq_price_watch_user_category"),
    )
    op.create_index("ix_price_watches_user_id", "price_watches", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_price_watches_user_id", table_name="price_watches")
    op.drop_table("price_watches")
