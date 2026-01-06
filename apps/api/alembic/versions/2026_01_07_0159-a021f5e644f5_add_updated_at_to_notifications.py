"""add_updated_at_to_notifications

Revision ID: a021f5e644f5
Revises: 17e3338d0c96
Create Date: 2026-01-07 01:59:53.705522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a021f5e644f5'
down_revision = '17e3338d0c96'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'notifications' AND column_name = 'updated_at')"
    ))
    column_exists = result.scalar()
    
    if not column_exists:
        op.add_column(
            'notifications',
            sa.Column(
                'updated_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=False
            )
        )
        
        op.execute(sa.text(
            "UPDATE notifications SET updated_at = created_at WHERE updated_at IS NULL"
        ))


def downgrade() -> None:
    op.drop_column('notifications', 'updated_at')

