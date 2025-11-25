"""
Схемы для модуля поддержки.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.support.domain.models import TicketStatus


class TicketCreate(BaseModel):
    """Создание тикета поддержки."""
    
    subject: str = Field(..., min_length=1, max_length=255, description="Тема тикета")
    body: str = Field(..., min_length=1, description="Описание проблемы")
    booking_id: Optional[UUID] = Field(None, description="ID связанного бронирования")


class TicketUpdate(BaseModel):
    """Обновление тикета."""
    
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Тема тикета")
    body: Optional[str] = Field(None, min_length=1, description="Описание проблемы")
    status: Optional[TicketStatus] = Field(None, description="Статус тикета")


class TicketResponse(BaseModel):
    """Ответ с информацией о тикете."""
    
    id: UUID = Field(..., description="ID тикета")
    user_id: UUID = Field(..., description="ID автора")
    booking_id: Optional[UUID] = Field(None, description="ID связанного бронирования")
    subject: str = Field(..., description="Тема")
    body: str = Field(..., description="Описание")
    status: TicketStatus = Field(..., description="Статус")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    # Дополнительная информация
    user_name: Optional[str] = Field(None, description="Имя автора")
    user_email: Optional[str] = Field(None, description="Email автора")
    
    class Config:
        from_attributes = True


class TicketList(BaseModel):
    """Список тикетов с пагинацией."""
    
    tickets: list[TicketResponse] = Field(..., description="Список тикетов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    page_size: int = Field(..., description="Размер страницы")


class TicketStatusUpdate(BaseModel):
    """Обновление статуса тикета."""
    
    status: TicketStatus = Field(..., description="Новый статус")


class TicketStats(BaseModel):
    """Статистика по тикетам."""
    
    total: int = Field(..., description="Всего тикетов")
    open: int = Field(..., description="Открытых")
    in_progress: int = Field(..., description="В работе")
    resolved: int = Field(..., description="Решенных")
    closed: int = Field(..., description="Закрытых")

