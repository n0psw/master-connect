"""
Pydantic схемы для модуля чата.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Создание сообщения."""
    text: str = Field(..., min_length=1, description="Текст сообщения")


class MessageResponse(BaseModel):
    """Ответ с сообщением."""
    id: UUID = Field(..., description="ID сообщения")
    dialog_id: UUID = Field(..., description="ID диалога")
    sender_id: UUID = Field(..., description="ID отправителя")
    text: Optional[str] = Field(None, description="Текст сообщения")
    file_url: Optional[str] = Field(None, description="URL вложения")
    is_read: bool = Field(..., description="Прочитано ли сообщение")
    created_at: datetime = Field(..., description="Дата создания")
    is_own: bool = Field(..., description="Принадлежит ли сообщение текущему пользователю")

    class Config:
        from_attributes = True


class DialogSummary(BaseModel):
    """Краткая информация о диалоге."""
    id: UUID = Field(..., description="ID диалога")
    booking_id: UUID = Field(..., description="ID бронирования")
    student_id: UUID = Field(..., description="ID студента")
    student_name: Optional[str] = Field(None, description="Имя студента")
    mentor_id: UUID = Field(..., description="ID ментора")
    mentor_name: Optional[str] = Field(None, description="Имя ментора")
    last_message_preview: Optional[str] = Field(None, description="Последнее сообщение")
    last_message_at: Optional[datetime] = Field(None, description="Время последнего сообщения")
    unread_count: int = Field(0, description="Количество непрочитанных сообщений")


class DialogListResponse(BaseModel):
    """Список диалогов пользователя."""
    dialogs: List[DialogSummary] = Field(default_factory=list, description="Диалоги пользователя")


class MessageListResponse(BaseModel):
    """Ответ со списком сообщений."""
    dialog: DialogSummary = Field(..., description="Информация о диалоге")
    messages: List[MessageResponse] = Field(default_factory=list, description="Сообщения диалога")



