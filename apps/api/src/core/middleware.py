"""
Middleware для обработки запросов.
"""
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .logging import generate_correlation_id, get_logger, set_correlation_id

logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления correlation ID в каждый запрос."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Генерируем или извлекаем correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
        set_correlation_id(correlation_id)
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Добавляем correlation ID в заголовки ответа
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Логируем входящий запрос
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            user_agent=request.headers.get("user-agent"),
            client_ip=self._get_client_ip(request),
        )
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Вычисляем время обработки
        duration = time.time() - start_time
        
        # Логируем ответ
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение IP адреса клиента."""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Используем IP клиента напрямую
        if request.client:
            return request.client.host
        
        return "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления заголовков безопасности."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Добавляем заголовки безопасности
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        return response


def setup_cors(app) -> None:
    """Настройка CORS."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID"],
    )


def setup_middleware(app) -> None:
    """Настройка всех middleware."""
    # Порядок важен: middleware выполняются в обратном порядке добавления
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    setup_cors(app)

