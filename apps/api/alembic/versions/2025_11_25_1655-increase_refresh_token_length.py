"""increase_refresh_token_length

Revision ID: a1b2c3d4e5f6
Revises: e073868af5c9
Create Date: 2025-11-25 16:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'e073868af5c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Изменяем тип поля token с VARCHAR(255) на TEXT
    op.alter_column('refresh_tokens', 'token',
                    existing_type=sa.String(length=255),
                    type_=sa.Text(),
                    existing_nullable=False)


def downgrade() -> None:
    # Откатываем обратно к VARCHAR(255)
    op.alter_column('refresh_tokens', 'token',
                    existing_type=sa.Text(),
                    type_=sa.String(length=255),
                    existing_nullable=False)

