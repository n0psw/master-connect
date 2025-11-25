"""
Domain модели для административных функций.
"""
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import BigInteger, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from modules.users.domain.models import User


class AuditLog(Base):
    """Журнал аудита действий администраторов."""
    
    # Переопределяем ID для использования bigint с автоинкрементом
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    
    # Кто выполнил действие
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Что было сделано
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # На какой сущности
    entity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(index=True)
    
    # Дополнительные метаданные
    meta_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Связи
    actor: Mapped[Optional["User"]] = relationship(
        "User",
        # back_populates="audit_logs",  # Временно отключено из-за cyclic dependencies
        foreign_keys=[actor_id]
    )
    
    def __str__(self) -> str:
        actor_name = self.actor.name if self.actor else "System"
        return f"{actor_name} {self.action} {self.entity}:{self.entity_id}"
    
    @classmethod
    def create_log(
        cls,
        actor_id: Optional[uuid.UUID],
        action: str,
        entity: str,
        entity_id: Optional[uuid.UUID] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> "AuditLog":
        """Создание записи аудита."""
        return cls(
            actor_id=actor_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            meta_json=meta or {}
        )
    
    @property
    def meta(self) -> Dict[str, Any]:
        """Получение метаданных."""
        return self.meta_json or {}
    
    def add_meta(self, key: str, value: Any) -> None:
        """Добавление метаданных."""
        if not self.meta_json:
            self.meta_json = {}
        self.meta_json[key] = value
