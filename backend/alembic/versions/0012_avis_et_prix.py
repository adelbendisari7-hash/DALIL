"""Avis vérifiés et historique des prix : empreinte du client sur les contacts, table `price_points` remplie avec
le prix actuel de chaque produit.

Revision ID: 0012
Revises: 0011
"""
from alembic import op
import sqlalchemy as sa

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("contact_events") as b:
        b.add_column(sa.Column("client_hash", sa.String(length=16), nullable=True))
        b.create_index("ix_contact_events_client_hash", ["client_hash"])
    op.create_table(
        "price_points",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("part_categories.id"), nullable=False),
        sa.Column("condition", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for col in ("product_id", "shop_id", "category_id", "recorded_at"):
        op.create_index(f"ix_price_points_{col}", "price_points", [col])
    # Point de départ : le prix actuel de chaque produit, daté de sa dernière confirmation
    op.execute(
        "INSERT INTO price_points (product_id, shop_id, category_id, condition, price, recorded_at) "
        "SELECT id, shop_id, category_id, COALESCE(condition, 'neuf'), price, COALESCE(price_confirmed_at, updated_at) "
        "FROM products WHERE price IS NOT NULL"
    )


def downgrade() -> None:
    for col in ("product_id", "shop_id", "category_id", "recorded_at"):
        op.drop_index(f"ix_price_points_{col}", table_name="price_points")
    op.drop_table("price_points")
    with op.batch_alter_table("contact_events") as b:
        b.drop_index("ix_contact_events_client_hash")
        b.drop_column("client_hash")
