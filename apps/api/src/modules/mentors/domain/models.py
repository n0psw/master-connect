"""
Domain модели для менторов.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.users.domain.models import User
    from modules.availability.domain.models import AvailabilityRule, TimeOff, MentorSettings
    from modules.bookings.domain.models import Booking
    from modules.reviews.domain.models import Review


class Mentor(Base):
    """Модель ментора."""
    
    # Переопределяем id как None, чтобы исключить его из таблицы
    id = None
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )
    
    # Профессиональная информация
    headline: Mapped[Optional[str]] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    
    # Цены за консультации (в тенге)
    price_30: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    price_45: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    price_60: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    
    # Специализация
    languages: Mapped[List[str]] = mapped_column(JSON, default=list)
    subjects: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Рейтинг
    rating_avg: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), 
        default=Decimal("0.00"), 
        nullable=False
    )
    rating_count: Mapped[int] = mapped_column(default=0, nullable=False)
    
    
    # Медиа
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Базовые поля (вручную, не наследуем от Base)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="mentor_profile")
    
    universities: Mapped[List["MentorUniversity"]] = relationship(
        "MentorUniversity",
        back_populates="mentor",
        cascade="all, delete-orphan"
    )
    
    availability_rules: Mapped[List["AvailabilityRule"]] = relationship(
        "AvailabilityRule",
        back_populates="mentor",
        cascade="all, delete-orphan"
    )
    
    time_offs: Mapped[List["TimeOff"]] = relationship(
        "TimeOff",
        back_populates="mentor",
        cascade="all, delete-orphan"
    )
    
    availability_settings: Mapped[Optional["MentorSettings"]] = relationship(
        "MentorSettings",
        back_populates="mentor",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="mentor",
        foreign_keys="Booking.mentor_id",
        passive_deletes=True
    )
    
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="mentor",
        cascade="all, delete-orphan"
    )
    
    def __str__(self) -> str:
        return f"Mentor: {self.user.name or self.user.email}"
    
    @property
    def country(self) -> Optional[str]:
        """Страна ментора из первого университета."""
        if self.universities:
            return self.universities[0].country
        return None
    
    @property
    def city(self) -> Optional[str]:
        """Город ментора из первого университета."""
        if self.universities:
            return self.universities[0].city
        return None


class MentorUniversity(Base):
    """Образование ментора."""
    
    # Собственный ID как primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mentors.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Информация об образовании
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(String(100))  # Bachelor, Master, PhD
    major: Mapped[Optional[str]] = mapped_column(String(255))   # Специальность
    
    # Годы обучения
    year_from: Mapped[Optional[int]] = mapped_column()
    year_to: Mapped[Optional[int]] = mapped_column()
    
    # Локация
    country: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Связи
    mentor: Mapped[Mentor] = relationship("Mentor", back_populates="universities")
    
    def __str__(self) -> str:
        return f"{self.university} - {self.major or 'Unknown'}"
