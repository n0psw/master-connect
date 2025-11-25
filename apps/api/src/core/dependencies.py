"""
FastAPI dependencies для аутентификации и авторизации.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import AuthenticationError, PermissionDeniedError
from .rbac import Permission, RoleChecker, has_permission
from db.session import get_db
from modules.auth.application.services import AuthService
from modules.users.domain.models import User, UserRole

# HTTP Bearer схема для JWT токенов
security = HTTPBearer(auto_error=False)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency для получения сервиса аутентификации."""
    return AuthService(db)


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Dependency для получения текущего пользователя (опционально).
    Возвращает None если токен не предоставлен или недействителен.
    """
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Dependency для получения текущего аутентифицированного пользователя."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency для получения активного пользователя."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """
    Decorator для создания dependency, требующего определенные роли.
    
    Args:
        allowed_roles: Список разрешенных ролей
    
    Returns:
        FastAPI dependency function
    """
    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется одна из ролей: {', '.join([role.value for role in allowed_roles])}"
            )
        return current_user
    
    return role_dependency


def require_permissions(required_permissions: List[Permission]):
    """
    Decorator для создания dependency, требующего определенные разрешения.
    
    Args:
        required_permissions: Список требуемых разрешений
    
    Returns:
        FastAPI dependency function
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        for permission in required_permissions:
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Недостаточно прав: требуется {permission.value}"
                )
        return current_user
    
    return permission_dependency


def require_role_checker(role_checker: RoleChecker):
    """
    Decorator для создания dependency с кастомным RoleChecker.
    
    Args:
        role_checker: Экземпляр RoleChecker
    
    Returns:
        FastAPI dependency function
    """
    def checker_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not role_checker(current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения данного действия"
            )
        return current_user
    
    return checker_dependency


# Предопределенные dependency functions для часто используемых ролей
get_current_admin = require_roles([UserRole.ADMIN])
get_current_mentor = require_roles([UserRole.MENTOR])
get_current_student = require_roles([UserRole.STUDENT])
get_current_mentor_or_admin = require_roles([UserRole.MENTOR, UserRole.ADMIN])
get_current_student_or_admin = require_roles([UserRole.STUDENT, UserRole.ADMIN])


def verify_resource_ownership(resource_user_id: UUID, current_user: User) -> bool:
    """
    Проверка, что пользователь является владельцем ресурса или администратором.
    
    Args:
        resource_user_id: ID пользователя-владельца ресурса
        current_user: Текущий пользователь
    
    Returns:
        bool: True если доступ разрешен
    """
    # Администратор имеет доступ ко всем ресурсам
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Пользователь имеет доступ только к своим ресурсам
    return current_user.id == resource_user_id


def verify_booking_access(booking, current_user: User) -> bool:
    """
    Проверка доступа к бронированию.
    
    Args:
        booking: Объект бронирования
        current_user: Текущий пользователь
    
    Returns:
        bool: True если доступ разрешен
    """
    # Администратор имеет доступ ко всем бронированиям
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Студент имеет доступ к своим бронированиям
    if current_user.role == UserRole.STUDENT and booking.student_id == current_user.id:
        return True
    
    # Ментор имеет доступ к бронированиям своих консультаций
    if current_user.role == UserRole.MENTOR and booking.mentor_id == current_user.id:
        return True
    
    return False


def verify_chat_access(dialog, current_user: User) -> bool:
    """
    Проверка доступа к чату.
    
    Args:
        dialog: Объект диалога
        current_user: Текущий пользователь
    
    Returns:
        bool: True если доступ разрешен
    """
    # Администратор имеет доступ ко всем чатам
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Участники диалога имеют доступ
    participant_ids = dialog.participant_ids
    return current_user.id in participant_ids


class CurrentUserInfo:
    """Информация о текущем пользователе для использования в endpoints."""
    
    def __init__(self, user: User):
        self.user = user
    
    @property
    def user_id(self) -> UUID:
        """Совместимость со старыми вызовами."""
        return self.user.id
    
    @property
    def id(self) -> UUID:
        return self.user.id
    
    @property
    def email(self) -> str:
        return self.user.email
    
    @property
    def role(self) -> UserRole:
        return self.user.role
    
    @property
    def is_admin(self) -> bool:
        return self.user.role == UserRole.ADMIN
    
    @property
    def is_mentor(self) -> bool:
        return self.user.role == UserRole.MENTOR
    
    @property
    def is_student(self) -> bool:
        return self.user.role == UserRole.STUDENT
    
    def has_permission(self, permission: Permission) -> bool:
        """Проверка наличия разрешения у пользователя."""
        return has_permission(self.user.role, permission)
    
    def can_access_resource(self, resource_user_id: UUID) -> bool:
        """Проверка доступа к ресурсу пользователя."""
        return verify_resource_ownership(resource_user_id, self.user)


async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> CurrentUserInfo:
    """Dependency для получения информации о текущем пользователе."""
    from core.logging import get_logger
    logger = get_logger(__name__)
    logger.debug("get_current_user_info called", user_id=str(current_user.id) if current_user else None)
    return CurrentUserInfo(current_user)

