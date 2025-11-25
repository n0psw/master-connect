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
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # Файловое хранилище (S3)
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str = "us-east-1"
    
    # Email
    EMAIL_SMTP_HOST: str
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: str
    EMAIL_SMTP_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_USE_TLS: bool = True
    
    # Google Calendar
    GOOGLE_CALENDAR_ENABLED: bool = False
    GOOGLE_SERVICE_ACCOUNT_FILE: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON_B64: Optional[str] = None
    GOOGLE_CALENDAR_ID: Optional[str] = None
    GOOGLE_CALENDAR_DELEGATED_USER: Optional[str] = None
    
    # Kaspi платежи
    KASPI_PAYMENT_URL: str
    
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
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Парсинг CORS origins."""
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            else:
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
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
