"""Référentiel véhicules : priorité d'affichage des modèles et véhicules demandés absents.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("models", schema=None) as batch_op:
        batch_op.add_column(sa.Column("priority", sa.Integer(), nullable=False, server_default="0"))
    op.create_table(
        "vehicle_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=60), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("engine", sa.String(length=60), nullable=True),
        sa.Column("client_hash", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("vehicle_requests")
    with op.batch_alter_table("models", schema=None) as batch_op:
        batch_op.drop_column("priority")
