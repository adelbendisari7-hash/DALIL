"""Équipe du magasin : employés avec leurs accès (le gérant décide de tout) et journal des actions.

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("added_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shop_id", "user_id", name="uq_shop_members"),
    )
    op.create_index("ix_shop_members_shop_id", "shop_members", ["shop_id"])
    op.create_index("ix_shop_members_user_id", "shop_members", ["user_id"])
    op.create_table(
        "shop_activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("target", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shop_activity_shop_id", "shop_activity", ["shop_id"])
    op.create_index("ix_shop_activity_created_at", "shop_activity", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_shop_activity_created_at", table_name="shop_activity")
    op.drop_index("ix_shop_activity_shop_id", table_name="shop_activity")
    op.drop_table("shop_activity")
    op.drop_index("ix_shop_members_user_id", table_name="shop_members")
    op.drop_index("ix_shop_members_shop_id", table_name="shop_members")
    op.drop_table("shop_members")
