"""
Pydantic схемы для модуля платежей.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class PaymentEvidenceCreate(BaseModel):
    """Схема для создания доказательства оплаты."""
    booking_id: UUID = Field(..., description="ID бронирования")
    comment_text: Optional[str] = Field(None, max_length=1000, description="Комментарий к оплате")
    receipt_file_url: Optional[str] = Field(None, description="URL файла квитанции")


class PaymentEvidenceResponse(BaseModel):
    """Схема ответа с информацией о доказательстве оплаты."""
    id: UUID = Field(..., description="ID доказательства")
    booking_id: UUID = Field(..., description="ID бронирования")
    created_by: UUID = Field(..., description="ID создателя")
    comment_text: Optional[str] = Field(None, description="Комментарий")
    receipt_file_url: Optional[str] = Field(None, description="URL файла")
    created_at: str = Field(..., description="Дата создания")
    
    # Связанные данные
    creator_name: Optional[str] = Field(None, description="Имя создателя")
    
    class Config:
        from_attributes = True


class PaymentEvidenceUpdate(BaseModel):
    """Схема для обновления доказательства оплаты."""
    comment_text: Optional[str] = Field(None, max_length=1000, description="Комментарий")

