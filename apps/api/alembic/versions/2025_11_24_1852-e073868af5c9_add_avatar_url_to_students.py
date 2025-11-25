"""add_avatar_url_to_students

Revision ID: e073868af5c9
Revises: fix_mentors_schema
Create Date: 2025-11-24 18:52:25.814182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e073868af5c9'
down_revision = 'fix_mentors_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('students', sa.Column('avatar_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('students', 'avatar_url')

