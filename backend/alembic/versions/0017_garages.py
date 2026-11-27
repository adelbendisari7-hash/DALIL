"""Spécialités des garages (mécaniciens proposés après un diagnostic).

Revision ID: 0017
Revises: 0016
"""
from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("shops") as b:
        b.add_column(sa.Column("specialties", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("shops") as b:
        b.drop_column("specialties")
