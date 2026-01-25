"""add booking_requests table

Revision ID: 20260125_add_booking_requests
Revises: b3f4a8c9d1e2
Create Date: 2026-01-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260125_add_booking_requests"
# реальный ID предыдущей миграции из файла b3f4a8c9d1e2_update_default_timezone.py
down_revision = "b3f4a8c9d1e2"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("booking_requests"):
        # Таблица уже есть (создана вручную/через create_all) — пропускаем
        return

    op.create_table(
        "booking_requests",
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("desired_starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("desired_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("student_reason", sa.String(length=500), nullable=True),
        sa.Column("admin_comment", sa.String(length=500), nullable=True),
        sa.Column("decided_by", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_booking_request_status", "booking_requests", ["status"])
    op.create_index("ix_booking_requests_booking_id", "booking_requests", ["booking_id"])
    op.create_index("ix_booking_requests_requested_by", "booking_requests", ["requested_by"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("booking_requests"):
        op.drop_index("ix_booking_requests_requested_by", table_name="booking_requests")
        op.drop_index("ix_booking_requests_booking_id", table_name="booking_requests")
        op.drop_index("idx_booking_request_status", table_name="booking_requests")
        op.drop_table("booking_requests")
