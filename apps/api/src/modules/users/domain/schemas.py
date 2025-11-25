"""
Pydantic схемы для модуля пользователей.
"""
from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from modules.users.domain.models import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    name: Optional[str] = Field(None, max_length=255, description="Имя пользователя")
    phone: Optional[str] = Field(None, max_length=50, description="Телефон")
    timezone: str = Field("UTC", description="Часовой пояс")
    locale: str = Field("ru", description="Язык интерфейса")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Валидация номера телефона."""
        if v and not v.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "").isdigit():
            raise ValueError("Некорректный формат номера телефона")
        return v


class UserCreate(UserBase):
    """Схема для создания пользователя."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль")
    role: UserRole = Field(..., description="Роль пользователя")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Валидация пароля."""
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_letter and has_digit):
            raise ValueError("Пароль должен содержать как минимум одну букву и одну цифру")
        
        return v


class UserUpdate(UserBase):
    """Схема для обновления пользователя."""
    is_active: Optional[bool] = Field(None, description="Статус активности")


class UserResponse(UserBase):
    """Схема ответа с информацией о пользователе."""
    id: UUID = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    role: UserRole = Field(..., description="Роль пользователя")
    is_active: bool = Field(..., description="Активен ли пользователь")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")
    
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """Схема списка пользователей."""
    users: list[UserResponse] = Field(..., description="Список пользователей")
    total: int = Field(..., description="Общее количество пользователей")
    page: int = Field(..., description="Номер страницы")
    page_size: int = Field(..., description="Размер страницы")


class StudentProfileBase(BaseModel):
    """Базовая схема профиля студента."""
    goals: Optional[str] = Field(None, description="Цели обучения")
    country: Optional[str] = Field(None, max_length=100, description="Страна")
    city: Optional[str] = Field(None, max_length=100, description="Город")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL аватара")


class StudentProfileCreate(StudentProfileBase):
    """Схема для создания профиля студента."""
    pass


class StudentProfileUpdate(StudentProfileBase):
    """Схема для обновления профиля студента."""
    pass


class StudentProfileResponse(StudentProfileBase):
    """Схема ответа с профилем студента."""
    user_id: UUID = Field(..., description="ID пользователя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")
    
    model_config = ConfigDict(from_attributes=True)


class UserWithProfile(UserResponse):
    """Пользователь с профилем."""
    student_profile: Optional[StudentProfileResponse] = Field(
        None, description="Профиль студента (если роль student)"
    )


class UserActivation(BaseModel):
    """Схема для активации/деактивации пользователя."""
    is_active: bool = Field(..., description="Статус активности")
    reason: Optional[str] = Field(None, description="Причина изменения статуса")


class UserStatsOverview(BaseModel):
    """Обзор статистики пользователей."""
    total_users: int = Field(..., description="Общее количество пользователей")
    active_users: int = Field(..., description="Количество активных пользователей")
    total_students: int = Field(..., description="Количество студентов")
    total_mentors: int = Field(..., description="Количество менторов")
    total_admins: int = Field(..., description="Количество администраторов")
    new_users_30d: int = Field(..., description="Новых пользователей за 30 дней")

