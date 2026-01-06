"""add_booking_created_notification_type

Revision ID: 17e3338d0c96
Revises: fix_notification_enum_casing_20251207
Create Date: 2026-01-07 00:52:35.886102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17e3338d0c96'
down_revision = 'fix_enum_casing'  # Updated to match fixed revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_CREATED';")


def downgrade() -> None:
    pass

