"""
Domain модели для системы отзывов.
"""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.users.domain.models import Student
    from modules.mentors.domain.models import Mentor
    from modules.bookings.domain.models import Booking


class Review(Base):
    """Модель отзыва о консультации."""
    
    # Связь с бронированием (один к одному)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Участники (дублируем для удобства запросов)
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mentors.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Содержание отзыва
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )  # 1-5 звезд
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Связи
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="review"
    )
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="reviews",
        foreign_keys=[student_id]
    )
    mentor: Mapped["Mentor"] = relationship(
        "Mentor",
        back_populates="reviews",
        foreign_keys=[mentor_id]
    )
    
    def __str__(self) -> str:
        return f"Review {self.rating}/5 for {self.mentor.user.name}"
    
    @property
    def is_positive(self) -> bool:
        """Проверка, является ли отзыв положительным (4-5 звезд)."""
        return self.rating >= 4
    
    @property
    def is_negative(self) -> bool:
        """Проверка, является ли отзыв отрицательным (1-2 звезды)."""
        return self.rating <= 2
    
    def validate_rating(self) -> bool:
        """Валидация рейтинга."""
        return 1 <= self.rating <= 5
