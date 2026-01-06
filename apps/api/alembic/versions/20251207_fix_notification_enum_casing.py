"""Normalize notification_type enum to upper-case values.

Revision ID: fix_notification_enum_casing_20251207
Revises: ef7d2cbe0dd0
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "fix_enum_casing"  # Shortened from fix_notification_enum_casing_20251207 (too long for VARCHAR(32))
down_revision = "ef7d2cbe0dd0"
branch_labels = None
depends_on = None


# Полный набор значений в верхнем регистре, соответствующий коду.
UPPER_VALUES = [
    "BOOKING_CREATED",
    "BOOKING_CONFIRMED",
    "BOOKING_CANCELLED",
    "BOOKING_RESCHEDULED",
    "BOOKING_REMINDER",
    "BOOKING_COMPLETED",
    "BOOKING_NO_SHOW",
    "BOOKING_EXPIRED",
    "PAYMENT_VERIFIED",
    "PAYMENT_REQUIRED",
    "REVIEW_RECEIVED",
    "REVIEW_CREATED",
    "MESSAGE_RECEIVED",
    "SUPPORT_TICKET_UPDATE",
    "SYSTEM_ANNOUNCEMENT",
    "ADMIN_MODERATION",
    "ADMIN_PAYMENT_QUEUE",
]


def upgrade() -> None:
    conn = op.get_bind()

    # Создаем временный enum с корректными значениями в верхнем регистре.
    values_sql = ", ".join(f"'{v}'" for v in UPPER_VALUES)
    conn.execute(sa.text(f"CREATE TYPE notification_type_new AS ENUM ({values_sql})"))

    # Переводим колонку на новый тип с приведением к верхнему регистру.
    conn.execute(
        sa.text(
            """
            ALTER TABLE notifications
            ALTER COLUMN type DROP DEFAULT,
            ALTER COLUMN type TYPE notification_type_new
                USING upper(type::text)::notification_type_new
            """
        )
    )

    # Удаляем старый тип и переименовываем новый в основной.
    conn.execute(sa.text("DROP TYPE notification_type"))
    conn.execute(sa.text("ALTER TYPE notification_type_new RENAME TO notification_type"))


def downgrade() -> None:
    conn = op.get_bind()

    # Воссоздаем нижний регистр для обратной совместимости (включая все значения).
    lower_values_sql = ", ".join(f"'{v.lower()}'" for v in UPPER_VALUES)
    conn.execute(sa.text(f"CREATE TYPE notification_type_old AS ENUM ({lower_values_sql})"))

    conn.execute(
        sa.text(
            """
            ALTER TABLE notifications
            ALTER COLUMN type DROP DEFAULT,
            ALTER COLUMN type TYPE notification_type_old
                USING lower(type::text)::notification_type_old
            """
        )
    )

    conn.execute(sa.text("DROP TYPE notification_type"))
    conn.execute(sa.text("ALTER TYPE notification_type_old RENAME TO notification_type"))
