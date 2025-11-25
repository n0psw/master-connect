"""
Модели для модуля уведомлений.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class NotificationType(str, Enum):
    """Типы уведомлений."""
    BOOKING_CREATED = "booking_created"  # Создано бронирование
    BOOKING_CONFIRMED = "booking_confirmed"  # Бронирование подтверждено
    BOOKING_CANCELLED = "booking_cancelled"  # Бронирование отменено
    BOOKING_RESCHEDULED = "booking_rescheduled"  # Бронирование перенесено
    BOOKING_REMINDER = "booking_reminder"  # Напоминание о консультации
    PAYMENT_VERIFIED = "payment_verified"  # Оплата подтверждена
    PAYMENT_REQUIRED = "payment_required"  # Требуется оплата
    REVIEW_RECEIVED = "review_received"  # Получен отзыв
    MESSAGE_RECEIVED = "message_received"  # Новое сообщение в чате
    SUPPORT_TICKET_UPDATE = "support_ticket_update"  # Обновление тикета поддержки
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # Системное объявление


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
        SQLEnum(NotificationType, name="notification_type"),
        nullable=False,
        index=True
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
        default=datetime.utcnow,
        nullable=False
    )
    
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<Notification {self.id}: {self.type} for user {self.user_id}>"

