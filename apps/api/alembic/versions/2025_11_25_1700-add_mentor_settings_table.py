"""add_mentor_settings_table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-25 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу mentor_settings
    op.create_table('mentor_settings',
    sa.Column('mentor_id', sa.UUID(), nullable=False),
    sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
    sa.Column('buffer_time_minutes', sa.Integer(), nullable=False, server_default='15'),
    sa.Column('max_bookings_per_day', sa.Integer(), nullable=False, server_default='8'),
    sa.Column('advance_booking_days', sa.Integer(), nullable=False, server_default='30'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentors.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('mentor_id')
    )
    op.create_index(op.f('ix_mentor_settings_mentor_id'), 'mentor_settings', ['mentor_id'], unique=False)


def downgrade() -> None:
    # Удаляем таблицу mentor_settings
    op.drop_index(op.f('ix_mentor_settings_mentor_id'), table_name='mentor_settings')
    op.drop_table('mentor_settings')

