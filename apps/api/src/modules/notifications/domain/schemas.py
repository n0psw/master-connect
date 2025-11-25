"""
Схемы для модуля уведомлений.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.notifications.domain.models import NotificationType


class NotificationResponse(BaseModel):
    """Ответ с информацией об уведомлении."""
    
    id: UUID = Field(..., description="ID уведомления")
    user_id: UUID = Field(..., description="ID пользователя")
    type: NotificationType = Field(..., description="Тип уведомления")
    title: str = Field(..., description="Заголовок уведомления")
    message: str = Field(..., description="Текст уведомления")
    is_read: bool = Field(..., description="Прочитано ли уведомление")
    related_entity_type: Optional[str] = Field(None, description="Тип связанной сущности")
    related_entity_id: Optional[UUID] = Field(None, description="ID связанной сущности")
    action_url: Optional[str] = Field(None, description="URL для перехода")
    created_at: datetime = Field(..., description="Дата создания")
    read_at: Optional[datetime] = Field(None, description="Дата прочтения")
    
    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    """Список уведомлений с пагинацией."""
    
    notifications: list[NotificationResponse] = Field(..., description="Список уведомлений")
    total: int = Field(..., description="Общее количество уведомлений")
    unread_count: int = Field(..., description="Количество непрочитанных уведомлений")
    page: int = Field(..., description="Номер текущей страницы")
    page_size: int = Field(..., description="Размер страницы")


class UnreadCount(BaseModel):
    """Количество непрочитанных уведомлений."""
    
    count: int = Field(..., description="Количество непрочитанных уведомлений")


class NotificationCreate(BaseModel):
    """Создание уведомления."""
    
    user_id: UUID = Field(..., description="ID пользователя")
    type: NotificationType = Field(..., description="Тип уведомления")
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок")
    message: str = Field(..., min_length=1, description="Текст уведомления")
    related_entity_type: Optional[str] = Field(None, max_length=50, description="Тип связанной сущности")
    related_entity_id: Optional[UUID] = Field(None, description="ID связанной сущности")
    action_url: Optional[str] = Field(None, max_length=500, description="URL для перехода")


class NotificationMarkRead(BaseModel):
    """Отметка уведомления как прочитанного."""
    
    notification_ids: list[UUID] = Field(..., description="ID уведомлений для отметки")

