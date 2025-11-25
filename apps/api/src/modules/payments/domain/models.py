"""
Domain модели для системы платежей.
"""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.bookings.domain.models import Booking
    from modules.users.domain.models import User


class PaymentEvidence(Base):
    """Доказательство оплаты (квитанция, скриншот и т.д.)."""
    
    # Связанное бронирование
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Кто загрузил доказательство
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Содержание
    comment_text: Mapped[Optional[str]] = mapped_column(Text)
    receipt_file_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Связи
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="payment_evidences",
        foreign_keys=[booking_id]
    )
    
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by]
    )
    
    def __str__(self) -> str:
        return f"Payment evidence for booking {self.booking_id}"
    
    @property
    def has_file(self) -> bool:
        """Проверка наличия файла."""
        return bool(self.receipt_file_url)
    
    @property
    def has_comment(self) -> bool:
        """Проверка наличия комментария."""
        return bool(self.comment_text and self.comment_text.strip())
