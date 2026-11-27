"""Carnet d'entretien : passages au garage (date, kilométrage, prix, garage, remarque) regroupant les opérations ;
opérations libres (« autre »). Chaque entretien déjà noté devient un passage.

Revision ID: 0013
Revises: 0012
"""
from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "maintenance_visits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_vehicle_id", sa.Integer(), sa.ForeignKey("user_vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("done_on", sa.Date(), nullable=False),
        sa.Column("km", sa.Integer(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("place", sa.String(length=120), nullable=True),
        sa.Column("note", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_visits_user_vehicle_id", "maintenance_visits", ["user_vehicle_id"])
    with op.batch_alter_table("maintenance_records") as b:
        b.add_column(sa.Column("visit_id", sa.Integer(), nullable=True))
        b.add_column(sa.Column("label", sa.String(length=80), nullable=True))
        b.create_foreign_key("fk_maintenance_records_visit", "maintenance_visits", ["visit_id"], ["id"], ondelete="CASCADE")
        b.create_index("ix_maintenance_records_visit_id", ["visit_id"])
    # Un passage par entretien déjà noté (même date et kilométrage)
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, user_vehicle_id, done_on, km, created_at FROM maintenance_records")).fetchall()
    for rid, vid, done_on, km, created in rows:
        new_id = conn.execute(sa.text(
            "INSERT INTO maintenance_visits (user_vehicle_id, done_on, km, created_at) VALUES (:v, :d, :k, :c) RETURNING id"),
            {"v": vid, "d": done_on, "k": km, "c": created}).scalar()
        conn.execute(sa.text("UPDATE maintenance_records SET visit_id = :n WHERE id = :r"), {"n": new_id, "r": rid})


def downgrade() -> None:
    with op.batch_alter_table("maintenance_records") as b:
        b.drop_index("ix_maintenance_records_visit_id")
        b.drop_constraint("fk_maintenance_records_visit", type_="foreignkey")
        b.drop_column("label")
        b.drop_column("visit_id")
    op.drop_index("ix_maintenance_visits_user_vehicle_id", table_name="maintenance_visits")
    op.drop_table("maintenance_visits")
