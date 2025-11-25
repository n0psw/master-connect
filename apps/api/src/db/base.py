"""
Базовая модель для SQLAlchemy.
"""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column


@as_declarative()
class Base:
    """Базовая модель для всех таблиц."""
    
    # Генерируем имя таблицы автоматически из имени класса
    @declared_attr
    def __tablename__(cls) -> str:
        # Преобразуем CamelCase в snake_case и добавляем суффикс 's'
        name = ""
        for i, char in enumerate(cls.__name__):
            if char.isupper() and i > 0:
                name += "_"
            name += char.lower()
        return name + "s" if not name.endswith("s") else name
    
    # Базовые поля для всех моделей
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
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
    
    def __repr__(self) -> str:
        """Строковое представление модели."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> dict[str, Any]:
        """Преобразование модели в словарь."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

