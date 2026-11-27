"""Entretien des voitures du compte client : entretiens notés (élément, kilométrage, date).

Revision ID: 0011
Revises: 0010
"""
from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_vehicle_id", sa.Integer(), sa.ForeignKey("user_vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item", sa.String(length=40), nullable=False),
        sa.Column("km", sa.Integer(), nullable=True),
        sa.Column("done_on", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_records_user_vehicle_id", "maintenance_records", ["user_vehicle_id"])


def downgrade() -> None:
    op.drop_index("ix_maintenance_records_user_vehicle_id", table_name="maintenance_records")
    op.drop_table("maintenance_records")
