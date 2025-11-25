"""
Pydantic схемы для модуля менторов.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from modules.users.domain.schemas import UserResponse


class MentorUniversityBase(BaseModel):
    """Базовая схема образования ментора."""
    university: str = Field(..., max_length=255, description="Название университета")
    degree: Optional[str] = Field(None, max_length=100, description="Степень (Bachelor, Master, PhD)")
    major: Optional[str] = Field(None, max_length=255, description="Специальность")
    year_from: Optional[int] = Field(None, ge=1900, le=2030, description="Год начала обучения")
    year_to: Optional[int] = Field(None, ge=1900, le=2030, description="Год окончания обучения")
    country: Optional[str] = Field(None, max_length=100, description="Страна")
    city: Optional[str] = Field(None, max_length=100, description="Город")
    
    @validator("year_to")
    def validate_years(cls, v, values):
        """Валидация годов обучения."""
        year_from = values.get("year_from")
        if v and year_from and v < year_from:
            raise ValueError("Год окончания не может быть раньше года начала обучения")
        return v


class MentorUniversityCreate(MentorUniversityBase):
    """Схема для создания образования ментора."""
    pass


class MentorUniversityUpdate(MentorUniversityBase):
    """Схема для обновления образования ментора."""
    university: Optional[str] = Field(None, max_length=255, description="Название университета")


class MentorUniversityResponse(MentorUniversityBase):
    """Схема ответа с образованием ментора."""
    id: UUID = Field(..., description="ID записи об образовании")
    mentor_id: UUID = Field(..., description="ID ментора")
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата последнего обновления")
    
    class Config:
        from_attributes = True


class MentorBase(BaseModel):
    """Базовая схема ментора."""
    headline: Optional[str] = Field(None, max_length=255, description="Заголовок профиля")
    bio: Optional[str] = Field(None, description="Описание ментора")
    price_30: Optional[Decimal] = Field(None, ge=0, description="Цена за 30-минутную консультацию")
    price_45: Optional[Decimal] = Field(None, ge=0, description="Цена за 45-минутную консультацию")
    price_60: Optional[Decimal] = Field(None, ge=0, description="Цена за 60-минутную консультацию")
    languages: List[str] = Field(default=[], description="Языки консультаций")
    subjects: List[str] = Field(default=[], description="Предметные области")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL аватара")
    
    @validator("languages")
    def validate_languages(cls, v):
        """Валидация языков."""
        if not isinstance(v, list):
            raise ValueError("Языки должны быть списком")
        
        # Убираем дубликаты и пустые строки
        languages = list(set(lang.strip() for lang in v if lang.strip()))
        
        # Разрешаем пустой список для существующих менторов
        return languages
    
    @validator("subjects")
    def validate_subjects(cls, v):
        """Валидация предметов."""
        if not isinstance(v, list):
            raise ValueError("Предметы должны быть списком")
        
        # Убираем дубликаты и пустые строки
        subjects = list(set(subj.strip() for subj in v if subj.strip()))
        
        return subjects


class MentorCreate(MentorBase):
    """Схема для создания ментора."""
    pass


class MentorUpdate(MentorBase):
    """Схема для обновления ментора."""
    pass


class MentorResponse(MentorBase):
    """Схема ответа с информацией о менторе."""
    user_id: UUID = Field(..., description="ID пользователя")
    rating_avg: Decimal = Field(..., description="Средний рейтинг")
    rating_count: int = Field(..., description="Количество отзывов")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")
    
    class Config:
        from_attributes = True


class MentorCard(BaseModel):
    """Карточка ментора для списка (краткая информация)."""
    id: UUID = Field(..., description="ID ментора")
    user_id: UUID = Field(..., description="ID пользователя (дубликат id для совместимости)")
    name: str = Field(..., description="Имя ментора")
    headline: Optional[str] = Field(None, description="Заголовок профиля")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    languages: List[str] = Field(..., description="Языки консультаций")
    subjects: List[str] = Field(..., description="Предметные области")
    universities: List[str] = Field(..., description="Университеты")
    price_30: Optional[Decimal] = Field(None, description="Цена за 30 минут")
    price_60: Optional[Decimal] = Field(None, description="Цена за 60 минут")
    rating_avg: Decimal = Field(..., description="Средний рейтинг")
    rating_count: int = Field(..., description="Количество отзывов")
    country: Optional[str] = Field(None, description="Страна")
    city: Optional[str] = Field(None, description="Город")


class MentorDetail(BaseModel):
    """Детальная информация о менторе."""
    mentor: MentorResponse = Field(..., description="Информация о менторе")
    user: UserResponse = Field(..., description="Информация о пользователе")
    universities: List[MentorUniversityResponse] = Field(..., description="Образование")
    reviews_count: int = Field(..., description="Количество отзывов")
    total_consultations: int = Field(..., description="Общее количество консультаций")
    completed_consultations: int = Field(..., description="Завершенные консультации")


class MentorList(BaseModel):
    """Список менторов."""
    mentors: List[MentorCard] = Field(..., description="Список менторов")
    total: int = Field(..., description="Общее количество менторов")
    page: int = Field(..., description="Номер страницы")
    page_size: int = Field(..., description="Размер страницы")




class MentorStats(BaseModel):
    """Статистика менторов."""
    total_mentors: int = Field(..., description="Общее количество менторов")
    active_mentors: int = Field(..., description="Количество активных менторов")
    average_rating: Optional[Decimal] = Field(None, description="Средний рейтинг всех менторов")
    total_consultations: int = Field(..., description="Общее количество консультаций")


# === АДМИНСКИЕ СХЕМЫ ===

class AdminMentorCreate(BaseModel):
    """Схема для создания ментора администратором."""
    # Данные пользователя
    email: str = Field(..., description="Email пользователя")
    name: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")
    phone: Optional[str] = Field(None, description="Телефон")
    timezone: str = Field(default="Asia/Almaty", description="Часовой пояс")
    locale: str = Field(default="ru", description="Локаль")
    
    # Данные профиля ментора
    headline: Optional[str] = Field(None, description="Заголовок профиля")
    bio: Optional[str] = Field(None, description="Биография")
    price_30: Optional[Decimal] = Field(None, description="Цена за 30 минут")
    price_45: Optional[Decimal] = Field(None, description="Цена за 45 минут")
    price_60: Optional[Decimal] = Field(None, description="Цена за 60 минут")
    languages: List[str] = Field(default_factory=list, description="Языки консультаций")
    subjects: List[str] = Field(default_factory=list, description="Предметные области")
    avatar_url: Optional[str] = Field(None, description="URL аватара")


class AdminMentorUpdate(BaseModel):
    """Схема для обновления ментора администратором."""
    # Данные пользователя
    name: Optional[str] = Field(None, description="Имя пользователя")
    phone: Optional[str] = Field(None, description="Телефон")
    timezone: Optional[str] = Field(None, description="Часовой пояс")
    locale: Optional[str] = Field(None, description="Локаль")
    is_active: Optional[bool] = Field(None, description="Активен ли пользователь")
    
    # Данные профиля ментора
    headline: Optional[str] = Field(None, description="Заголовок профиля")
    bio: Optional[str] = Field(None, description="Биография")
    price_30: Optional[Decimal] = Field(None, description="Цена за 30 минут")
    price_45: Optional[Decimal] = Field(None, description="Цена за 45 минут")
    price_60: Optional[Decimal] = Field(None, description="Цена за 60 минут")
    languages: Optional[List[str]] = Field(None, description="Языки консультаций")
    subjects: Optional[List[str]] = Field(None, description="Предметные области")
    avatar_url: Optional[str] = Field(None, description="URL аватара")


class AdminMentorDetail(BaseModel):
    """Детальная информация о менторе для администратора."""
    mentor: MentorResponse = Field(..., description="Информация о менторе")
    user: UserResponse = Field(..., description="Информация о пользователе")
    universities: List[MentorUniversityResponse] = Field(..., description="Образование")
    reviews_count: int = Field(..., description="Количество отзывов")
    total_consultations: int = Field(..., description="Общее количество консультаций")
    completed_consultations: int = Field(..., description="Завершенные консультации")


class MentorFilters(BaseModel):
    """Фильтры для поиска менторов."""
    languages: Optional[List[str]] = Field(None, description="Языки")
    subjects: Optional[List[str]] = Field(None, description="Предметные области")
    countries: Optional[List[str]] = Field(None, description="Страны")
    price_min: Optional[Decimal] = Field(None, ge=0, description="Минимальная цена")
    price_max: Optional[Decimal] = Field(None, ge=0, description="Максимальная цена")
    rating_min: Optional[Decimal] = Field(None, ge=0, le=5, description="Минимальный рейтинг")
    has_availability: Optional[bool] = Field(None, description="Есть доступные слоты")


class MentorSortOptions(str, Enum):
    """Опции сортировки менторов."""
    RATING_DESC = "rating_desc"
    RATING_ASC = "rating_asc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    REVIEWS_COUNT_DESC = "reviews_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"


# Дополнительные схемы для университетов

class UniversitySuggestion(BaseModel):
    """Предложение университета для автокомплита."""
    name: str = Field(..., description="Название университета")
    country: Optional[str] = Field(None, description="Страна")
    city: Optional[str] = Field(None, description="Город")
    count: int = Field(..., description="Количество менторов из этого университета")


class PopularSubjects(BaseModel):
    """Популярные предметы."""
    subjects: List[str] = Field(..., description="Список популярных предметов")


class PopularLanguages(BaseModel):
    """Популярные языки."""
    languages: List[str] = Field(..., description="Список популярных языков")
