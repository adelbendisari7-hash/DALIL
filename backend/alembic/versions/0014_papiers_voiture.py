"""Papiers des voitures (contrôle technique, assurance : fait le, valable jusqu'au) ; magasin DALIL d'un passage
au garage.

Revision ID: 0014
Revises: 0013
"""
from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicle_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_vehicle_id", sa.Integer(), sa.ForeignKey("user_vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("done_on", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("note", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vehicle_documents_user_vehicle_id", "vehicle_documents", ["user_vehicle_id"])
    with op.batch_alter_table("maintenance_visits") as b:
        b.add_column(sa.Column("shop_id", sa.Integer(), nullable=True))
        b.create_foreign_key("fk_maintenance_visits_shop", "shops", ["shop_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    with op.batch_alter_table("maintenance_visits") as b:
        b.drop_constraint("fk_maintenance_visits_shop", type_="foreignkey")
        b.drop_column("shop_id")
    op.drop_index("ix_vehicle_documents_user_vehicle_id", table_name="vehicle_documents")
    op.drop_table("vehicle_documents")
