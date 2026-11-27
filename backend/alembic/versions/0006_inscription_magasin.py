"""Inscription guidée des magasins : repère, horaires structurés (« ouvert maintenant »), fermeture exceptionnelle,
motif de refus, téléphone du magasin unique, revendications de fiche en attente de vérification.

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("shops", schema=None) as batch_op:
        batch_op.add_column(sa.Column("landmark", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("opening", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("closed_until", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("closed_note", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("reject_reason", sa.String(length=255), nullable=True))
        # Téléphone du magasin unique (aucun doublon dans la base au 27/11/2026) ; plusieurs fiches sans numéro restent possibles
        batch_op.drop_index("ix_shops_phone")
        batch_op.create_index("ix_shops_phone", ["phone"], unique=True)
    op.create_table(
        "shop_claims",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shop_claims_shop_id", "shop_claims", ["shop_id"])


def downgrade() -> None:
    op.drop_index("ix_shop_claims_shop_id", table_name="shop_claims")
    op.drop_table("shop_claims")
    with op.batch_alter_table("shops", schema=None) as batch_op:
        batch_op.drop_index("ix_shops_phone")
        batch_op.create_index("ix_shops_phone", ["phone"], unique=False)
        for col in ("reject_reason", "closed_note", "closed_until", "opening", "landmark"):
            batch_op.drop_column(col)
