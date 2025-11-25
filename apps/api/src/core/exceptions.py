"""
Базовые исключения и обработчики ошибок.
"""
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .config import settings
from .logging import get_correlation_id, get_logger

logger = get_logger(__name__)


class MasterConnectException(Exception):
    """Базовое исключение приложения."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ValidationException(MasterConnectException):
    """Ошибка валидации."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class NotFoundError(MasterConnectException):
    """Ресурс не найден."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} с идентификатором '{identifier}' не найден",
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PermissionDeniedError(MasterConnectException):
    """Недостаточно прав доступа."""
    
    def __init__(self, message: str = "Недостаточно прав доступа"):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class AuthenticationError(MasterConnectException):
    """Ошибка аутентификации."""
    
    def __init__(self, message: str = "Не авторизован"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ConflictError(MasterConnectException):
    """Конфликт данных."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            details=details,
            status_code=status.HTTP_409_CONFLICT,
        )


class BusinessLogicError(MasterConnectException):
    """Ошибка бизнес-логики."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ExternalServiceError(MasterConnectException):
    """Ошибка внешнего сервиса."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"Ошибка сервиса {service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class RateLimitError(MasterConnectException):
    """Превышен лимит запросов."""
    
    def __init__(self, message: str = "Превышен лимит запросов"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> Dict[str, Any]:
    """Создание стандартного ответа об ошибке."""
    return {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "request_id": get_correlation_id(),
        }
    }


async def masterconnect_exception_handler(
    request: Request, exc: MasterConnectException
) -> JSONResponse:
    """Обработчик исключений приложения."""
    logger.error(
        "Application exception",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Обработчик HTTP исключений."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
        ),
    )


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации Pydantic."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        "Validation error",
        errors=errors,
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            error_code="VALIDATION_ERROR",
            message="Ошибка валидации данных",
            details={"errors": errors},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик всех остальных исключений."""
    import traceback
    
    error_message = str(exc)
    error_type = type(exc).__name__
    
    logger.error(
        "Unhandled exception",
        exception=error_message,
        exception_type=error_type,
        path=request.url.path,
        method=request.method,
        exc_info=exc,
    )
    
    details = {}
    if settings.DEBUG:
        details = {
            "exception_type": error_type,
            "exception_message": error_message,
            "traceback": traceback.format_exc().split('\n') if settings.DEBUG else None,
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message=error_message if settings.DEBUG else "Внутренняя ошибка сервера",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ),
    )

