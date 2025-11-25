"""
Domain модели для пользователей.
"""
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.auth.domain.models import RefreshToken
    from modules.bookings.domain.models import Booking
    from modules.reviews.domain.models import Review
    from modules.chat.domain.models import Message
    from modules.support.domain.models import SupportTicket
    from modules.admin.domain.models import AuditLog
    from modules.mentors.domain.models import Mentor


class UserRole(str, Enum):
    """Роли пользователей."""
    STUDENT = "student"
    MENTOR = "mentor"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя."""
    
    # Основная информация
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Роль и статус
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Персональная информация
    name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Локализация
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    locale: Mapped[str] = mapped_column(String(10), default="ru", nullable=False)
    
    # Связи с профилями
    student_profile: Mapped[Optional["Student"]] = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    mentor_profile: Mapped[Optional["Mentor"]] = relationship(
        "Mentor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # Связи с другими сущностями
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        "SupportTicket",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="sender",
        foreign_keys="Message.sender_id"
    )
    
    # audit_logs: Mapped[list["AuditLog"]] = relationship(
    #     "AuditLog",
    #     back_populates="actor",
    #     foreign_keys="AuditLog.actor_id"
    # )
    
    def __str__(self) -> str:
        return f"{self.name or self.email} ({self.role})"
    
    @property
    def is_student(self) -> bool:
        """Проверка, является ли пользователь студентом."""
        return self.role == UserRole.STUDENT
    
    @property
    def is_mentor(self) -> bool:
        """Проверка, является ли пользователь ментором."""
        return self.role == UserRole.MENTOR
    
    @property
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь админом."""
        return self.role == UserRole.ADMIN


class Student(Base):
    """Профиль студента."""
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )
    
    # Цели и интересы
    goals: Mapped[Optional[str]] = mapped_column(Text)
    
    # Локация
    country: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Медиа
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Связи
    user: Mapped[User] = relationship("User", back_populates="student_profile")
    
    # bookings: Mapped[list["Booking"]] = relationship(
    #     "Booking",
    #     back_populates="student",
    #     foreign_keys="Booking.student_id"
    # )
    
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    
    def __str__(self) -> str:
        return f"Student: {self.user.name or self.user.email}"
