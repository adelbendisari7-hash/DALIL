"""Catalogue plus rapide : date de dernière confirmation du prix et du stock d'un produit (« prix confirmé il y a
N jours », rappel des prix anciens).

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("price_confirmed_at", sa.DateTime(timezone=True), nullable=True))
    # Produits existants : leur dernière modification vaut confirmation
    op.execute("UPDATE products SET price_confirmed_at = updated_at")


def downgrade() -> None:
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("price_confirmed_at")
