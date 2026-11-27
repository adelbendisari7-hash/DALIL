"""Suivi des demandes par le client : jeton secret (suivi sans compte) et date de dernière lecture des réponses.

Revision ID: 0010
Revises: 0009
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("part_requests", schema=None) as batch_op:
        batch_op.add_column(sa.Column("token", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("seen_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("part_requests", schema=None) as batch_op:
        batch_op.drop_column("seen_at")
        batch_op.drop_column("token")
