"""
Domain модели для системных настроек.
"""
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class GlobalSettings(Base):
    """Глобальные настройки системы."""
    
    # Используем фиксированный ID для единственной записи
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1
    )
    
    # Платежные настройки
    kaspi_payment_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="https://pay.kaspi.kz/pay/default"
    )
    
    # Email настройки
    email_from: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="noreply@masterconnect.kz"
    )
    
    # Настройки уведомлений
    reminder_24h_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_1h_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Настройки брони
    booking_hold_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False
    )
    
    # Общие настройки
    platform_name: Mapped[str] = mapped_column(
        String(100),
        default="MasterConnect",
        nullable=False
    )
    
    support_email: Mapped[str] = mapped_column(
        String(255),
        default="support@masterconnect.kz",
        nullable=False
    )
    
    terms_url: Mapped[str] = mapped_column(
        String(500),
        default="https://masterconnect.kz/terms",
        nullable=False
    )
    
    privacy_url: Mapped[str] = mapped_column(
        String(500),
        default="https://masterconnect.kz/privacy",
        nullable=False
    )
    
    # Дополнительные настройки в JSON
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    maintenance_message: Mapped[str] = mapped_column(
        Text,
        default="Система временно недоступна. Приносим свои извинения.",
        nullable=False
    )
    
    def __str__(self) -> str:
        return f"GlobalSettings: {self.platform_name}"
    
    @classmethod
    def get_defaults(cls) -> dict:
        """Получение настроек по умолчанию."""
        return {
            "id": 1,
            "kaspi_payment_url": "https://pay.kaspi.kz/pay/default",
            "email_from": "noreply@masterconnect.kz",
            "reminder_24h_enabled": True,
            "reminder_1h_enabled": True,
            "booking_hold_duration_minutes": 10,
            "platform_name": "MasterConnect",
            "support_email": "support@masterconnect.kz",
            "terms_url": "https://masterconnect.kz/terms",
            "privacy_url": "https://masterconnect.kz/privacy",
            "maintenance_mode": False,
            "maintenance_message": "Система временно недоступна. Приносим свои извинения."
        }
