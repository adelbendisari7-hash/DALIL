"""Photo jointe à une demande de pièce.

Revision ID: 0015
Revises: 0014
"""
from alembic import op
import sqlalchemy as sa

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("part_requests") as b:
        b.add_column(sa.Column("photo_url", sa.String(length=255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("part_requests") as b:
        b.drop_column("photo_url")
