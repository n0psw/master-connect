"""
Domain модели для системы поддержки.
"""
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.users.domain.models import User
    from modules.bookings.domain.models import Booking


class TicketStatus(str, Enum):
    """Статусы тикетов поддержки."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class SupportTicket(Base):
    """Тикет службы поддержки."""
    
    # Автор тикета
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Связанное бронирование (опционально)
    booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("bookings.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Содержание тикета
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Статус
    status: Mapped[TicketStatus] = mapped_column(
        String(20),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True
    )
    
    # Связи
    user: Mapped["User"] = relationship(
        "User",
        back_populates="support_tickets",
        foreign_keys=[user_id]
    )
    
    booking: Mapped[Optional["Booking"]] = relationship(
        "Booking",
        foreign_keys=[booking_id]
    )
    
    def __str__(self) -> str:
        return f"Ticket #{self.id}: {self.subject}"
    
    @property
    def is_open(self) -> bool:
        """Проверка, открыт ли тикет."""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
    
    @property
    def is_closed(self) -> bool:
        """Проверка, закрыт ли тикет."""
        return self.status == TicketStatus.CLOSED
    
    def can_transition_to(self, new_status: TicketStatus) -> bool:
        """Проверка возможности смены статуса."""
        transitions = {
            TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED],
            TicketStatus.IN_PROGRESS: [TicketStatus.OPEN, TicketStatus.RESOLVED, TicketStatus.CLOSED],
            TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],
            TicketStatus.CLOSED: []
        }
        
        return new_status in transitions.get(self.status, [])
