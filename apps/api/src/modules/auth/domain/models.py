"""
Domain модели для аутентификации.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.users.domain.models import User


class RefreshToken(Base):
    """Модель refresh токена."""
    
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    device_info: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
    
    def __str__(self) -> str:
        return f"RefreshToken for {self.user.email}"
    
    @property
    def is_expired(self) -> bool:
        """Проверка истечения токена."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Проверка валидности токена."""
        return not self.is_revoked and not self.is_expired
