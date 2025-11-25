"""
Domain модели для системы чата.
"""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.bookings.domain.models import Booking
    from modules.users.domain.models import User


class Dialog(Base):
    """Диалог между студентом и ментором."""
    
    # Связь с бронированием (один к одному)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Статус диалога
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Связи
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="dialog"
    )
    
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="dialog",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __str__(self) -> str:
        return f"Dialog for booking {self.booking_id}"
    
    @property
    def participant_ids(self) -> tuple[uuid.UUID, uuid.UUID]:
        """ID участников диалога."""
        return (self.booking.student_id, self.booking.mentor_id)
    
    def can_send_message(self, user_id: uuid.UUID) -> bool:
        """Проверка, может ли пользователь отправлять сообщения."""
        if self.is_blocked:
            return False
        
        # Только участники диалога могут отправлять сообщения
        return user_id in self.participant_ids


class Message(Base):
    """Сообщение в диалоге."""
    
    dialog_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dialogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Содержание сообщения
    text: Mapped[Optional[str]] = mapped_column(Text)
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Статус прочтения
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Связи
    dialog: Mapped[Dialog] = relationship(
        "Dialog",
        back_populates="messages"
    )
    
    sender: Mapped["User"] = relationship(
        "User",
        back_populates="sent_messages",
        foreign_keys=[sender_id]
    )
    
    def __str__(self) -> str:
        content = self.text[:50] if self.text else "[File]"
        return f"Message from {self.sender.name}: {content}"
    
    @property
    def has_content(self) -> bool:
        """Проверка, есть ли контент в сообщении."""
        return bool(self.text or self.file_url)
    
    @property
    def is_file_message(self) -> bool:
        """Проверка, является ли сообщение файлом."""
        return bool(self.file_url)
    
    def mark_as_read(self) -> None:
        """Пометить сообщение как прочитанное."""
        self.is_read = True
