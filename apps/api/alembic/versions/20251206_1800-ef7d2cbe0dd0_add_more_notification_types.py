"""Add additional notification types for reviews and admin

Revision ID: ef7d2cbe0dd0
Revises: 970e64f393f9
Create Date: 2025-12-06 18:00:00
"""

from alembic import op

revision = "ef7d2cbe0dd0"
down_revision = "970e64f393f9"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'REVIEW_CREATED';")
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'ADMIN_MODERATION';")
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'ADMIN_PAYMENT_QUEUE';")
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_EXPIRED';")
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_REMINDER';")


def downgrade():
    # Enum rollback is not supported without recreating type; leave as no-op.
    pass

