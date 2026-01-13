"""update_default_timezone

Revision ID: b3f4a8c9d1e2
Revises: a021f5e644f5
Create Date: 2026-01-08 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b3f4a8c9d1e2'
down_revision = 'a021f5e644f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text(
        "UPDATE users SET timezone = 'Asia/Almaty' "
        "WHERE timezone IS NULL OR timezone = 'UTC' OR timezone = 'Etc/GMT-5'"
    ))


def downgrade() -> None:
    pass




