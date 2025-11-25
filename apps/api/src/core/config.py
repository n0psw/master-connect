"""
Конфигурация приложения и настройки окружения.
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Основные настройки
    APP_ENV: str = "development"
    APP_NAME: str = "MasterConnect API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    API_PREFIX: str = "/api/v1"
    
    # JWT настройки
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRES_DAYS: int = 30
    
    # База данных
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS (парсится в валидаторе из строки в список)
    # Используем строку как тип, чтобы pydantic не пытался парсить как JSON
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    # Файловое хранилище (S3) - опционально, если не используется
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"
    
    # Email - опционально, если не используется
    EMAIL_SMTP_HOST: Optional[str] = None
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: Optional[str] = None
    EMAIL_SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_USE_TLS: bool = True
    
    # Google Calendar
    GOOGLE_CALENDAR_ENABLED: bool = False
    GOOGLE_SERVICE_ACCOUNT_FILE: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON_B64: Optional[str] = None
    GOOGLE_CALENDAR_ID: Optional[str] = None
    GOOGLE_CALENDAR_DELEGATED_USER: Optional[str] = None
    
    # Kaspi платежи - опционально, можно указать дефолтное значение
    KASPI_PAYMENT_URL: str = "https://pay.kaspi.kz/pay/default"
    
    # Уведомления
    REMINDER_24H_ENABLED: bool = True
    REMINDER_1H_ENABLED: bool = True
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Настройки загрузки файлов
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "pdf,jpg,jpeg,png,docx"
    
    # Настройки брони (время на оплату после создания бронирования)
    BOOKING_HOLD_DURATION_MINUTES: int = 30
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Парсинг CORS origins из строки в список."""
        v = self.BACKEND_CORS_ORIGINS
        if v is None:
            return ["http://localhost:3000"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v or v == "[]":
                return ["http://localhost:3000"]
            if v.startswith("["):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if item]
                    return ["http://localhost:3000"]
                except (json.JSONDecodeError, ValueError, TypeError):
                    return [i.strip() for i in v.strip("[]\"").split(",") if i.strip()]
            return [i.strip() for i in v.split(",") if i.strip()]
        return ["http://localhost:3000"]
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Валидация URL базы данных."""
        allowed = (
            "postgresql://",
            "postgresql+psycopg://",
            "postgresql+psycopg2://",
            "sqlite+aiosqlite://",
        )
        if not v.startswith(allowed):
            raise ValueError(
                "DATABASE_URL должен быть PostgreSQL или SQLite (sqlite+aiosqlite://)"
            )
        return v


@lru_cache()
def get_settings() -> Settings:
    """Получение настроек (с кешированием)."""
    return Settings()


settings = get_settings()
