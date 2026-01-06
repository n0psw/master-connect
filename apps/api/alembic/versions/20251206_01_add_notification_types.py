"""Add new notification types for message and booking status

Revision ID: add_notification_types_20251206
Revises: 
Create Date: 2025-12-06
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_notification_types_20251206"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем новые значения в enum notification_type
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'MESSAGE_RECEIVED';")
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_COMPLETED';")
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_NO_SHOW';")


def downgrade():
    # Откат enum значений в PostgreSQL не поддерживается без пересоздания типа.
    # Оставляем no-op downgrade.
    pass

