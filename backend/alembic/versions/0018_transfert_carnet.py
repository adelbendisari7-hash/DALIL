"""Carnet transmis à la revente : codes de transfert créés par le vendeur.

Revision ID: 0018
Revises: 0017
"""
from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicle_transfers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_vehicle_id", sa.Integer(), sa.ForeignKey("user_vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("include_prices", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vehicle_transfers_user_vehicle_id", "vehicle_transfers", ["user_vehicle_id"])
    op.create_index("ix_vehicle_transfers_code_hash", "vehicle_transfers", ["code_hash"])


def downgrade() -> None:
    op.drop_index("ix_vehicle_transfers_code_hash", table_name="vehicle_transfers")
    op.drop_index("ix_vehicle_transfers_user_vehicle_id", table_name="vehicle_transfers")
    op.drop_table("vehicle_transfers")
