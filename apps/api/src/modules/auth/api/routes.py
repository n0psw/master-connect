"""
API роуты для модуля аутентификации.
"""
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_auth_service, get_current_active_user
from core.exceptions import AuthenticationError, BusinessLogicError
from core.logging import get_logger
from db.session import get_db
from modules.auth.application.services import AuthService
from modules.auth.domain.schemas import (
    AuthResponse,
    ErrorResponse,
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    TokenPair,
    UserInfo,
)
from modules.users.domain.models import User

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Аутентификация"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Регистрация нового пользователя в системе с выбором роли (student/mentor)",
    responses={
        201: {"description": "Пользователь успешно зарегистрирован"},
        400: {"description": "Ошибка валидации данных", "model": ErrorResponse},
        409: {"description": "Пользователь с таким email уже существует", "model": ErrorResponse},
        422: {"description": "Ошибка валидации", "model": ErrorResponse},
    }
)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """
    Регистрация нового пользователя.
    
    - **email**: Email адрес пользователя (уникальный)
    - **password**: Пароль (минимум 8 символов, должен содержать буквы и цифры)
    - **name**: Имя пользователя
    - **role**: Роль пользователя (student, mentor)
    - **phone**: Номер телефона (опционально)
    - **timezone**: Часовой пояс (по умолчанию UTC)
    - **locale**: Язык интерфейса (по умолчанию ru)
    """
    try:
        response = await auth_service.register_user(register_data)
        logger.info("User registered via API", email=register_data.email, role=register_data.role)
        return response
    
    except BusinessLogicError as e:
        logger.warning("Registration failed", email=register_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Unexpected error during registration", email=register_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Вход в систему",
    description="Аутентификация пользователя по email и паролю",
    responses={
        200: {"description": "Успешная аутентификация"},
        401: {"description": "Неверные учетные данные", "model": ErrorResponse},
        403: {"description": "Аккаунт деактивирован", "model": ErrorResponse},
        422: {"description": "Ошибка валидации", "model": ErrorResponse},
    }
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """
    Аутентификация пользователя.
    
    - **email**: Email адрес пользователя
    - **password**: Пароль пользователя
    
    Возвращает access токен и информацию о пользователе.
    """
    try:
        response = await auth_service.login_user(login_data)
        logger.info("User logged in via API", email=login_data.email)
        return response
    
    except AuthenticationError as e:
        logger.warning("Login failed", email=login_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except Exception as e:
        logger.error("Unexpected error during login", email=login_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Обновление access токена",
    description="Получение нового access токена с помощью refresh токена",
    responses={
        200: {"description": "Токен успешно обновлен"},
        401: {"description": "Неверный или истекший refresh токен", "model": ErrorResponse},
        422: {"description": "Ошибка валидации", "model": ErrorResponse},
    }
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenPair:
    """
    Обновление access токена.
    
    - **refresh_token**: Действующий refresh токен
    
    Возвращает новый access токен.
    """
    try:
        response = await auth_service.refresh_access_token(refresh_data.refresh_token)
        logger.info("Token refreshed via API")
        return response
    
    except AuthenticationError as e:
        logger.warning("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except Exception as e:
        logger.error("Unexpected error during token refresh", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы",
    description="Отзыв refresh токена и выход из системы",
    responses={
        204: {"description": "Успешный выход из системы"},
        401: {"description": "Требуется авторизация", "model": ErrorResponse},
    }
)
async def logout(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """
    Выход из системы.
    
    - **refresh_token**: Refresh токен для отзыва
    
    Отзывает указанный refresh токен.
    """
    try:
        await auth_service.revoke_refresh_token(refresh_data.refresh_token)
        logger.info("User logged out via API")
    
    except Exception as e:
        logger.error("Unexpected error during logout", error=str(e))
        # Не возвращаем ошибку для logout - лучше молча завершить операцию


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из всех устройств",
    description="Отзыв всех refresh токенов пользователя",
    responses={
        204: {"description": "Успешный выход из всех устройств"},
        401: {"description": "Требуется авторизация", "model": ErrorResponse},
    }
)
async def logout_all(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """
    Выход из всех устройств.
    
    Отзывает все refresh токены текущего пользователя.
    """
    try:
        revoked_count = await auth_service.revoke_all_user_tokens(current_user.id)
        logger.info("User logged out from all devices", user_id=current_user.id, revoked_count=revoked_count)
    
    except Exception as e:
        logger.error("Unexpected error during logout all", user_id=current_user.id, error=str(e))
        # Не возвращаем ошибку для logout - лучше молча завершить операцию


@router.get(
    "/me",
    response_model=UserInfo,
    summary="Информация о текущем пользователе",
    description="Получение информации о текущем аутентифицированном пользователе",
    responses={
        200: {"description": "Информация о пользователе"},
        401: {"description": "Требуется авторизация", "model": ErrorResponse},
        403: {"description": "Аккаунт деактивирован", "model": ErrorResponse},
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserInfo:
    """
    Получение информации о текущем пользователе.
    
    Возвращает подробную информацию о текущем аутентифицированном пользователе.
    """
    return UserInfo.from_orm(current_user)


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Запрос на сброс пароля",
    description="Отправка письма с инструкциями для сброса пароля",
    responses={
        204: {"description": "Письмо отправлено (если email существует)"},
        422: {"description": "Ошибка валидации", "model": ErrorResponse},
    }
)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """
    Запрос на сброс пароля.
    
    - **email**: Email адрес пользователя
    
    Отправляет письмо с инструкциями для сброса пароля.
    Всегда возвращает 204, независимо от того, существует ли email в системе.
    """
    await auth_service.request_password_reset(reset_request.email)
    logger.info("Password reset requested", email=reset_request.email)
    

@router.post(
    "/password-reset/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Подтверждение сброса пароля",
    description="Установка нового пароля по токену из email",
    responses={
        204: {"description": "Пароль успешно изменен"},
        400: {"description": "Неверный или истекший токен", "model": ErrorResponse},
        422: {"description": "Ошибка валидации", "model": ErrorResponse},
    }
)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """
    Подтверждение сброса пароля.
    
    - **token**: Токен из email для сброса пароля
    - **new_password**: Новый пароль
    
    Устанавливает новый пароль пользователю.
"""
    await auth_service.confirm_password_reset(
        reset_confirm.token,
        reset_confirm.new_password
    )
    logger.info("Password reset confirmed")


@router.post(
    "/password/change",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Смена пароля",
    description="Смена пароля для аутентифицированного пользователя",
    responses={
        204: {"description": "Пароль успешно изменен"},
        400: {"description": "Неверный текущий пароль", "model": ErrorResponse},
        401: {"description": "Требуется авторизация", "model": ErrorResponse},
        422: {"description": "Ошибка валидации", "model": ErrorResponse},
    }
)
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> None:
    """
    Смена пароля.
    
    - **current_password**: Текущий пароль пользователя
    - **new_password**: Новый пароль
    
    Изменяет пароль для текущего пользователя.
    """
    await auth_service.change_password(
        current_user.id,
        password_change.current_password,
        password_change.new_password
    )
    logger.info("Password change requested", user_id=current_user.id)


@router.get(
    "/health",
    summary="Проверка работоспособности модуля аутентификации",
    description="Endpoint для проверки работоспособности модуля аутентификации",
    responses={
        200: {"description": "Модуль работает корректно"},
    }
)
async def auth_health_check() -> Dict[str, Any]:
    """Проверка работоспособности модуля аутентификации."""
    return {
        "status": "healthy",
        "module": "auth",
        "timestamp": "2024-09-10T18:00:00Z",
        "features": [
            "registration",
            "login",
            "token_refresh",
            "logout",
            "password_reset",
            "rbac"
        ]
    }

