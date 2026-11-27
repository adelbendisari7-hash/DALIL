"""Compte client : prénom, nom, e-mail, commune, date de naissance ; voitures du client (matricule unique),
signalements de matricule déjà pris, voiture rattachée à chaque diagnostic.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("first_name", sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column("last_name", sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column("email", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("commune_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("birth_date", sa.Date(), nullable=True))
        batch_op.create_foreign_key("fk_users_commune", "communes", ["commune_id"], ["id"])
    op.create_table(
        "user_vehicles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plate", sa.String(length=16), nullable=False),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("vehicle_variants.id"), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("nickname", sa.String(length=60), nullable=True),
        sa.Column("mileage_km", sa.Integer(), nullable=True),
        sa.Column("vin", sa.String(length=17), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plate", name="uq_user_vehicles_plate"),
    )
    op.create_index("ix_user_vehicles_user_id", "user_vehicles", ["user_id"])
    op.create_table(
        "plate_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plate", sa.String(length=16), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plate_reports_plate", "plate_reports", ["plate"])
    with op.batch_alter_table("diagnosis_sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_vehicle_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_sessions_user_vehicle", "user_vehicles", ["user_vehicle_id"], ["id"],
                                    ondelete="SET NULL")


def downgrade() -> None:
    with op.batch_alter_table("diagnosis_sessions", schema=None) as batch_op:
        batch_op.drop_constraint("fk_sessions_user_vehicle", type_="foreignkey")
        batch_op.drop_column("user_vehicle_id")
    op.drop_index("ix_plate_reports_plate", table_name="plate_reports")
    op.drop_table("plate_reports")
    op.drop_index("ix_user_vehicles_user_id", table_name="user_vehicles")
    op.drop_table("user_vehicles")
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("fk_users_commune", type_="foreignkey")
        for col in ("birth_date", "commune_id", "email", "last_name", "first_name"):
            batch_op.drop_column(col)
