"""Statistiques du magasin : apparitions dans un classement et fiches ouvertes (une fois par client et par jour, sans
donnée personnelle), pièces cherchées (position arrondie à environ 1 km).

Revision ID: 0009
Revises: 0008
"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("client_hash", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shop_events_shop_id", "shop_events", ["shop_id"])
    op.create_index("ix_shop_events_created_at", "shop_events", ["created_at"])
    op.create_table(
        "search_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("part_categories.id"), nullable=False),
        sa.Column("brand_id", sa.Integer(), sa.ForeignKey("brands.id"), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_events_category_id", "search_events", ["category_id"])
    op.create_index("ix_search_events_created_at", "search_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_search_events_created_at", table_name="search_events")
    op.drop_index("ix_search_events_category_id", table_name="search_events")
    op.drop_table("search_events")
    op.drop_index("ix_shop_events_created_at", table_name="shop_events")
    op.drop_index("ix_shop_events_shop_id", table_name="shop_events")
    op.drop_table("shop_events")
