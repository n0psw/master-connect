"""
Pydantic схемы для модуля отзывов.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ReviewCreate(BaseModel):
    """Схема для создания отзыва."""
    booking_id: UUID = Field(..., description="ID бронирования")
    rating: int = Field(..., ge=1, le=5, description="Рейтинг от 1 до 5")
    text: str = Field(..., min_length=10, max_length=2000, description="Текст отзыва")
    
    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        """Валидация рейтинга."""
        if not 1 <= v <= 5:
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return v


class ReviewUpdate(BaseModel):
    """Схема для обновления отзыва."""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Рейтинг от 1 до 5")
    text: Optional[str] = Field(None, min_length=10, max_length=2000, description="Текст отзыва")


class ReviewResponse(BaseModel):
    """Схема ответа с информацией об отзыве."""
    id: UUID = Field(..., description="ID отзыва")
    booking_id: UUID = Field(..., description="ID бронирования")
    student_id: UUID = Field(..., description="ID студента")
    mentor_id: UUID = Field(..., description="ID ментора")
    rating: int = Field(..., description="Рейтинг")
    text: str = Field(..., description="Текст отзыва")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    # Дополнительная информация
    student_name: Optional[str] = Field(None, description="Имя студента")
    student_avatar_url: Optional[str] = Field(None, description="Аватар студента")
    mentor_name: Optional[str] = Field(None, description="Имя ментора")
    mentor_avatar_url: Optional[str] = Field(None, description="Аватар ментора")
    
    model_config = ConfigDict(from_attributes=True)


class ReviewList(BaseModel):
    """Список отзывов."""
    reviews: list[ReviewResponse] = Field(..., description="Список отзывов")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    page_size: int = Field(..., description="Размер страницы")


class ReviewStats(BaseModel):
    """Статистика отзывов."""
    total_reviews: int = Field(..., description="Общее количество отзывов")
    average_rating: float = Field(..., description="Средний рейтинг")
    rating_distribution: dict[int, int] = Field(..., description="Распределение по рейтингу")
    positive_reviews: int = Field(..., description="Положительные отзывы (4-5)")
    negative_reviews: int = Field(..., description="Отрицательные отзывы (1-2)")

