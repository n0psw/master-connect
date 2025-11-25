"""
Конфигурация структурированного логирования.
"""
import logging
import logging.config
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict

import structlog
from structlog.typing import EventDict, Processor

from .config import settings

# Context для correlation ID
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Добавление correlation ID в логи."""
    if correlation_id_value := correlation_id.get():
        event_dict["correlation_id"] = correlation_id_value
    return event_dict


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Добавление контекста приложения."""
    event_dict["app"] = settings.APP_NAME
    event_dict["version"] = settings.APP_VERSION
    event_dict["env"] = settings.APP_ENV
    return event_dict


def setup_logging() -> None:
    """Настройка логирования для приложения."""
    
    # Определяем процессоры для structlog
    processors: list[Processor] = [
        add_correlation_id,
        add_app_context,
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if settings.APP_ENV == "development":
        # В development используем красивый вывод в консоль
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    else:
        # В production используем JSON формат
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])
    
    # Настройка structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Настройка стандартного logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "console" if settings.APP_ENV == "development" else "json",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "INFO" if settings.DATABASE_ECHO else "WARNING",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> structlog.BoundLogger:
    """Получение логгера с именем."""
    return structlog.get_logger(name)


def generate_correlation_id() -> str:
    """Генерация correlation ID."""
    return str(uuid.uuid4())


def set_correlation_id(correlation_id_value: str) -> None:
    """Установка correlation ID в контекст."""
    correlation_id.set(correlation_id_value)


def get_correlation_id() -> str:
    """Получение текущего correlation ID."""
    return correlation_id.get()

