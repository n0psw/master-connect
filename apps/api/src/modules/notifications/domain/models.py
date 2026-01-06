"""
Модели для модуля уведомлений.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class NotificationType(str, Enum):
    """Типы уведомлений."""
    BOOKING_CREATED = "BOOKING_CREATED"  # Создано бронирование
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"  # Бронирование подтверждено
    BOOKING_CANCELLED = "BOOKING_CANCELLED"  # Бронирование отменено
    BOOKING_RESCHEDULED = "BOOKING_RESCHEDULED"  # Бронирование перенесено
    BOOKING_REMINDER = "BOOKING_REMINDER"  # Напоминание о консультации
    BOOKING_COMPLETED = "BOOKING_COMPLETED"  # Консультация завершена
    BOOKING_NO_SHOW = "BOOKING_NO_SHOW"  # Неявка
    PAYMENT_VERIFIED = "PAYMENT_VERIFIED"  # Оплата подтверждена
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"  # Требуется оплата
    REVIEW_RECEIVED = "REVIEW_RECEIVED"  # Получен отзыв
    REVIEW_CREATED = "REVIEW_CREATED"  # Отзыв создан (для получателя)
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"  # Новое сообщение в чате
    SUPPORT_TICKET_UPDATE = "SUPPORT_TICKET_UPDATE"  # Обновление тикета поддержки
    SYSTEM_ANNOUNCEMENT = "SYSTEM_ANNOUNCEMENT"  # Системное объявление
    ADMIN_MODERATION = "ADMIN_MODERATION"  # Новая задача модерации
    ADMIN_PAYMENT_QUEUE = "ADMIN_PAYMENT_QUEUE"  # Новая задача в платежной очереди
    BOOKING_EXPIRED = "BOOKING_EXPIRED"  # HOLD истек


class Notification(Base):
    """Модель уведомления."""
    
    __tablename__ = "notifications"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(
            NotificationType,
            name="notification_type",
            values_callable=lambda obj: [e.name for e in obj],
        ),
        nullable=False,
        index=True,
    )
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # ID связанной сущности (booking_id, message_id, etc.)
    related_entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    related_entity_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True
    )
    
    # URL для перехода при клике
    action_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<Notification {self.id}: {self.type} for user {self.user_id}>"

