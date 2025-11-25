"""Fix mentors table schema - single primary key

Revision ID: fix_mentors_schema
Revises: 53a19d0b709e
Create Date: 2025-10-22 18:05:31.422486

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'fix_mentors_schema'
down_revision = '53a19d0b709e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Пересоздать таблицу mentors с правильной схемой."""
    
    # Проверяем, существует ли таблица mentor_universitys и удаляем её, если есть
    # (она зависит от mentors)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'mentor_universitys' in inspector.get_table_names():
        op.drop_table('mentor_universitys')
    
    # Удаляем старую таблицу mentors
    op.drop_table('mentors')
    
    # Создаем новую таблицу mentors с user_id как единственным primary key
    op.create_table('mentors',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('price_30', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('price_45', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('price_60', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=False),
        sa.Column('subjects', sa.JSON(), nullable=False),
        sa.Column('rating_avg', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('rating_count', sa.Integer(), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Создаем индекс для user_id (хотя он уже primary key)
    op.create_index(op.f('ix_mentors_user_id'), 'mentors', ['user_id'], unique=False)
    
    # Пересоздаем таблицу mentor_universitys с правильным внешним ключом
    op.create_table('mentor_universitys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('mentor_id', sa.UUID(), nullable=False),
        sa.Column('university', sa.String(length=255), nullable=False),
        sa.Column('degree', sa.String(length=100), nullable=True),
        sa.Column('major', sa.String(length=255), nullable=True),
        sa.Column('year_from', sa.Integer(), nullable=True),
        sa.Column('year_to', sa.Integer(), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['mentor_id'], ['mentors.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentor_universitys_id'), 'mentor_universitys', ['id'], unique=False)
    op.create_index(op.f('ix_mentor_universitys_mentor_id'), 'mentor_universitys', ['mentor_id'], unique=False)


def downgrade() -> None:
    """Откат к старой схеме."""
    
    # Удаляем таблицу mentor_universitys
    op.drop_table('mentor_universitys')
    
    # Удаляем новую таблицу mentors
    op.drop_table('mentors')
    
    # Восстанавливаем старую схему с составным primary key
    op.create_table('mentors',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('price_30', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('price_45', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('price_60', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=False),
        sa.Column('subjects', sa.JSON(), nullable=False),
        sa.Column('rating_avg', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('rating_count', sa.Integer(), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'id')
    )
    
    op.create_index(op.f('ix_mentors_id'), 'mentors', ['id'], unique=False)

