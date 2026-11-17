"""Empreinte du client sur les retours (anti-abus du score « pièce trouvée »).

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("feedback", schema=None) as batch_op:
        batch_op.add_column(sa.Column("client_hash", sa.String(length=16), nullable=True))
        batch_op.create_index(batch_op.f("ix_feedback_client_hash"), ["client_hash"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("feedback", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_feedback_client_hash"))
        batch_op.drop_column("client_hash")
