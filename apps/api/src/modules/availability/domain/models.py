"""
Domain модели для управления доступностью менторов.
"""
import uuid
from datetime import datetime, time, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.mentors.domain.models import Mentor


class AvailabilityRule(Base):
    """Правило доступности ментора по дням недели."""
    
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mentors.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # День недели (0 = понедельник, 6 = воскресенье)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Время работы
    time_start: Mapped[time] = mapped_column(Time, nullable=False)
    time_end: Mapped[time] = mapped_column(Time, nullable=False)
    
    # Длительность слота в минутах
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Буфер между слотами в минутах
    buffer_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    
    # Перерывы в JSON формате
    # Пример: [{"start": "12:00", "end": "13:00", "title": "Обед"}]
    breaks_json: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, 
        default=list, 
        nullable=False
    )
    
    # Связи
    mentor: Mapped["Mentor"] = relationship("Mentor", back_populates="availability_rules")
    
    def __str__(self) -> str:
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        return f"{weekdays[self.weekday]}: {self.time_start}-{self.time_end}"
    
    @property
    def breaks(self) -> List[Dict[str, str]]:
        """Получение перерывов."""
        return self.breaks_json or []
    
    def add_break(self, start: str, end: str, title: str = "Перерыв") -> None:
        """Добавление перерыва."""
        if not self.breaks_json:
            self.breaks_json = []
        
        self.breaks_json.append({
            "start": start,
            "end": end,
            "title": title
        })
    
    def validate_time_range(self) -> bool:
        """Валидация временного диапазона."""
        return self.time_start < self.time_end


class MentorSettings(Base):
    """Настройки доступности ментора."""
    
    # Исключаем id из наследования базового класса, так как используем mentor_id как PK
    __mapper_args__ = {
        "primary_key": ["mentor_id"],
        "exclude_properties": ["id"]
    }
    
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mentors.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Часовой пояс
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    
    # Настройки расписания
    buffer_time_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    max_bookings_per_day: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    advance_booking_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Связи
    mentor: Mapped["Mentor"] = relationship("Mentor", back_populates="availability_settings")
    
    def __str__(self) -> str:
        return f"MentorSettings: {self.timezone}, buffer={self.buffer_time_minutes}min"


class TimeOff(Base):
    """Отсутствие ментора (отпуск, болезнь и т.д.)."""
    
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mentors.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Период отсутствия
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
    
    # Причина отсутствия
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Связи
    mentor: Mapped["Mentor"] = relationship("Mentor", back_populates="time_offs")
    
    def __str__(self) -> str:
        return f"TimeOff: {self.starts_at.date()} - {self.ends_at.date()}"
    
    def validate_date_range(self) -> bool:
        """Валидация временного диапазона."""
        return self.starts_at < self.ends_at
    
    def overlaps_with(self, other: "TimeOff") -> bool:
        """Проверка пересечения с другим периодом отсутствия."""
        return (
            self.starts_at < other.ends_at and
            self.ends_at > other.starts_at
        )
