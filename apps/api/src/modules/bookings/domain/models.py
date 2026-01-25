"""
Domain модели для системы бронирования.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.users.domain.models import Student, User
    from modules.mentors.domain.models import Mentor
    from modules.reviews.domain.models import Review
from modules.chat.domain.models import Dialog
from modules.payments.domain.models import PaymentEvidence
from modules.users.domain.models import User


class BookingStatus(str, Enum):
    """Статусы бронирования."""
    HOLD = "HOLD"                               # Временная бронь (10 мин)
    AWAITING_VERIFICATION = "AWAITING_VERIFICATION"  # Ожидает подтверждения оплаты
    CONFIRMED = "CONFIRMED"                     # Подтверждено
    CANCELLED = "CANCELLED"                     # Отменено
    COMPLETED = "COMPLETED"                     # Завершено
    REJECTED = "REJECTED"                       # Отклонено админом
    NO_SHOW_STUDENT = "NO_SHOW_STUDENT"        # Студент не пришел
    NO_SHOW_MENTOR = "NO_SHOW_MENTOR"          # Ментор не пришел
    EXPIRED = "EXPIRED"                         # Истекло время HOLD


class Booking(Base):
    """Модель бронирования консультации."""
    
    # Участники
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
    
    # Время консультации
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Финансы
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="KZT", nullable=False)
    
    # Статус
    status: Mapped[BookingStatus] = mapped_column(
        String(25),
        default=BookingStatus.HOLD,
        nullable=False,
        index=True
    )
    
    # Google Meet/Zoom информация
    meeting_url: Mapped[Optional[str]] = mapped_column(String(500))
    meeting_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    zoom_join_url: Mapped[Optional[str]] = mapped_column(String(500))
    zoom_start_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Форма intake (JSON)
    intake_form: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Информация об оплате
    payment_note: Mapped[Optional[str]] = mapped_column(Text)
    receipt_file_url: Mapped[Optional[str]] = mapped_column(String(500))
    payment_status: Mapped[str] = mapped_column(String(20), default="UNPAID", nullable=False)
    payment_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Связи
    student: Mapped["Student"] = relationship(
        "Student",
        foreign_keys=[student_id]
    )
    mentor: Mapped["Mentor"] = relationship(
        "Mentor",
        back_populates="bookings",
        foreign_keys=[mentor_id]
    )
    
    review: Mapped[Optional["Review"]] = relationship(
        "Review",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    dialog: Mapped[Optional["Dialog"]] = relationship(
        "Dialog",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    payment_evidences: Mapped[list["PaymentEvidence"]] = relationship(
        "PaymentEvidence",
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    requests: Mapped[list["BookingRequest"]] = relationship(
        "BookingRequest",
        back_populates="booking",
        cascade="all, delete-orphan"
    )
    
    def __str__(self) -> str:
        return f"Booking {self.id}: {self.mentor.user.name} -> {self.student.user.name}"
    
    @property
    def is_active(self) -> bool:
        """Проверка, является ли бронь активной (блокирует слот)."""
        return self.status in [
            BookingStatus.HOLD,
            BookingStatus.AWAITING_VERIFICATION,
            BookingStatus.CONFIRMED
        ]
    
    @property
    def is_modifiable(self) -> bool:
        """Можно ли изменить бронь."""
        return self.status in [
            BookingStatus.HOLD,
            BookingStatus.AWAITING_VERIFICATION,
            BookingStatus.CONFIRMED
        ]
    
    @property
    def can_be_reviewed(self) -> bool:
        """Можно ли оставить отзыв."""
        return self.status == BookingStatus.COMPLETED and self.review is None
    
    @property
    def is_confirmed(self) -> bool:
        """Подтверждена ли бронь."""
        return self.status == BookingStatus.CONFIRMED
    
    @property
    def is_completed(self) -> bool:
        """Завершена ли бронь."""
        return self.status == BookingStatus.COMPLETED
    
    def can_transition_to(self, new_status: BookingStatus) -> bool:
        """Проверка возможности перехода в новый статус."""
        transitions = {
            BookingStatus.HOLD: [
                BookingStatus.AWAITING_VERIFICATION,
                BookingStatus.EXPIRED,
                BookingStatus.CANCELLED
            ],
            BookingStatus.AWAITING_VERIFICATION: [
                BookingStatus.CONFIRMED,
                BookingStatus.REJECTED,
                BookingStatus.CANCELLED
            ],
            BookingStatus.CONFIRMED: [
                BookingStatus.COMPLETED,
                BookingStatus.NO_SHOW_STUDENT,
                BookingStatus.NO_SHOW_MENTOR,
                BookingStatus.CANCELLED
            ],
            BookingStatus.REJECTED: [],
            BookingStatus.CANCELLED: [],
            BookingStatus.COMPLETED: [],
            BookingStatus.NO_SHOW_STUDENT: [],
            BookingStatus.NO_SHOW_MENTOR: [],
            BookingStatus.EXPIRED: []
        }
        
        return new_status in transitions.get(self.status, [])


# Индексы для производительности
Index("idx_booking_mentor_time", Booking.mentor_id, Booking.starts_at)
Index("idx_booking_student_time", Booking.student_id, Booking.starts_at)
Index("idx_booking_status_time", Booking.status, Booking.starts_at)

# Уникальный индекс для предотвращения двойного бронирования
# Один ментор не может иметь пересекающиеся активные брони
Index(
    "idx_booking_unique_slot",
    Booking.mentor_id,
    Booking.starts_at,
    unique=True,
    postgresql_where=(
        Booking.status.in_([
            BookingStatus.HOLD,
            BookingStatus.AWAITING_VERIFICATION,
            BookingStatus.CONFIRMED
        ])
    )
)

# Индекс для фильтрации по updated_at (используется в moderation queue)
Index("idx_booking_updated_at", Booking.updated_at)

# === Booking requests (cancel/reschedule with admin approval) ===
class BookingRequestType(str, Enum):
    CANCEL = "CANCEL"
    RESCHEDULE = "RESCHEDULE"


class BookingRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class BookingRequest(Base):
    """Запрос на отмену или перенос, требующий решения администратора."""

    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    requested_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    type: Mapped[BookingRequestType] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[BookingRequestStatus] = mapped_column(String(20), default=BookingRequestStatus.PENDING, nullable=False, index=True)

    desired_starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    desired_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    student_reason: Mapped[Optional[str]] = mapped_column(String(500))
    admin_comment: Mapped[Optional[str]] = mapped_column(String(500))
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    booking: Mapped["Booking"] = relationship("Booking", back_populates="requests")
    requester: Mapped["User"] = relationship("User", foreign_keys=[requested_by])
    admin: Mapped[Optional["User"]] = relationship("User", foreign_keys=[decided_by])

    __table_args__ = (
        Index("idx_booking_request_status", "status"),
    )
