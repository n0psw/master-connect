"""
Pydantic схемы для модуля аутентификации.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Any
from datetime import datetime

from modules.users.domain.models import UserRole


class LoginRequest(BaseModel):
    """Запрос на вход в систему."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль")


class RegisterRequest(BaseModel):
    """Запрос на регистрацию."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль")
    name: str = Field(..., min_length=1, max_length=255, description="Имя пользователя")
    role: UserRole = Field(..., description="Роль пользователя")
    phone: Optional[str] = Field(None, max_length=50, description="Телефон")
    timezone: str = Field("Asia/Almaty", description="Часовой пояс")
    locale: str = Field("ru", description="Язык интерфейса")
    
    @validator("password")
    def validate_password(cls, v):
        """Валидация пароля."""
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        
        # Проверка на наличие букв и цифр
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_letter and has_digit):
            raise ValueError("Пароль должен содержать как минимум одну букву и одну цифру")
        
        return v
    
    @validator("phone")
    def validate_phone(cls, v):
        """Валидация номера телефона."""
        if v and not v.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "").isdigit():
            raise ValueError("Некорректный формат номера телефона")
        return v


class TokenPair(BaseModel):
    """Пара токенов для аутентификации."""
    access_token: str = Field(..., description="JWT access токен")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field("bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена в секундах")

class TokenResponse(BaseModel):
    """Устаревший ответ только с access токеном (сохранен для совместимости)."""
    access_token: str = Field(..., description="JWT access токен")
    token_type: str = Field("bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена."""
    refresh_token: str = Field(..., description="Refresh токен")


class UserInfo(BaseModel):
    """Информация о пользователе."""
    id: UUID = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    name: Optional[str] = Field(None, description="Имя пользователя")
    role: UserRole = Field(..., description="Роль пользователя")
    phone: Optional[str] = Field(None, description="Телефон")
    timezone: str = Field(..., description="Часовой пояс")
    locale: str = Field(..., description="Язык интерфейса")
    is_active: bool = Field(..., description="Активен ли пользователь")
    created_at: Any = Field(..., description="Дата создания")
    
    @validator('created_at', pre=True, always=True)
    def serialize_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v else None
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Полный ответ при аутентификации."""
    user: UserInfo = Field(..., description="Информация о пользователе")
    tokens: TokenPair = Field(..., description="Пара токенов (access и refresh)")


class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля."""
    email: EmailStr = Field(..., description="Email пользователя")


class PasswordResetConfirm(BaseModel):
    """Подтверждение сброса пароля."""
    token: str = Field(..., description="Токен для сброса пароля")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    
    @validator("new_password")
    def validate_password(cls, v):
        """Валидация нового пароля."""
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_letter and has_digit):
            raise ValueError("Пароль должен содержать как минимум одну букву и одну цифру")
        
        return v


class PasswordChangeRequest(BaseModel):
    """Запрос на смену пароля (для авторизованного пользователя)."""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    
    @validator("new_password")
    def validate_password(cls, v):
        """Валидация нового пароля."""
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_letter and has_digit):
            raise ValueError("Пароль должен содержать как минимум одну букву и одну цифру")
        
        return v


class RefreshTokenInfo(BaseModel):
    """Информация о refresh токене."""
    id: UUID = Field(..., description="ID токена")
    user_id: UUID = Field(..., description="ID пользователя")
    expires_at: str = Field(..., description="Дата истечения")
    device_info: Optional[str] = Field(None, description="Информация об устройстве")
    is_revoked: bool = Field(..., description="Отозван ли токен")
    created_at: str = Field(..., description="Дата создания")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке."""
    error: dict = Field(..., description="Детали ошибки")
    
    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: Optional[dict] = None
    ) -> "ErrorResponse":
        """Создание ответа об ошибке."""
        return cls(
            error={
                "code": code,
                "message": message,
                "details": details or {}
            }
        )

