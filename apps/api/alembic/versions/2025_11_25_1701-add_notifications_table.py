"""add_notifications_table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-11-25 17:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Проверяем, существует ли enum, и создаем только если его нет
    conn = op.get_bind()
    enum_exists = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notification_type')"
    )).scalar()
    
    if not enum_exists:
        # Создаем enum для типа уведомления только если его нет
        notification_type_enum = postgresql.ENUM(
            'booking_created',
            'booking_confirmed',
            'booking_cancelled',
            'booking_rescheduled',
            'booking_reminder',
            'payment_verified',
            'payment_required',
            'review_received',
            'message_received',
            'support_ticket_update',
            'system_announcement',
            name='notification_type',
            create_type=False  # Устанавливаем False, так как мы управляем созданием вручную
        )
        notification_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Используем существующий enum для колонки
    notification_type_enum = postgresql.ENUM(
        'booking_created',
        'booking_confirmed',
        'booking_cancelled',
        'booking_rescheduled',
        'booking_reminder',
        'payment_verified',
        'payment_required',
        'review_received',
        'message_received',
        'support_ticket_update',
        'system_announcement',
        name='notification_type',
        create_type=False  # Не создаем, только используем
    )
    
    # Создаем таблицу notifications
    op.create_table('notifications',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('type', notification_type_enum, nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('related_entity_type', sa.String(length=50), nullable=True),
    sa.Column('related_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('action_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_type'), 'notifications', ['type'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)


def downgrade() -> None:
    # Удаляем таблицу notifications
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
    
    # Удаляем enum
    notification_type_enum = postgresql.ENUM(
        name='notification_type',
        create_type=False
    )
    notification_type_enum.drop(op.get_bind(), checkfirst=True)

