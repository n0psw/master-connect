"""
API роуты для модуля пользователей.
"""
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.dependencies import (
    get_current_active_user,
    get_current_admin,
    get_current_user_info,
    CurrentUserInfo,
    verify_resource_ownership,
)
from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from core.rbac import Permission
from db.session import get_db
from modules.users.application.services import UserService
from modules.users.domain.models import User, UserRole
from modules.users.domain.schemas import (
    StudentProfileResponse,
    StudentProfileUpdate,
    UserActivation,
    UserCreate,
    UserList,
    UserResponse,
    UserStatsOverview,
    UserUpdate,
    UserWithProfile,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Пользователи"])


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency для получения сервиса пользователей."""
    return UserService(db)


async def get_student_profile_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency для получения сервиса пользователя."""
    return UserService(db)


@router.get(
    "/me",
    response_model=UserWithProfile,
    summary="Мой профиль",
    description="Получение информации о текущем пользователе с профилем",
    responses={
        200: {"description": "Информация о пользователе"},
        401: {"description": "Требуется авторизация"},
    }
)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserWithProfile:
    """Получение своего профиля."""
    try:
        profile = await user_service.get_user_by_id(current_user.id, include_profile=True)
        return profile
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    except Exception as e:
        logger.error("Error getting user profile", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/me",
    response_model=UserWithProfile,
    summary="Обновление моего профиля",
    description="Обновление информации о текущем пользователе",
    responses={
        200: {"description": "Профиль обновлен"},
        401: {"description": "Требуется авторизация"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserWithProfile:
    """Обновление своего профиля."""
    try:
        updated_user = await user_service.update_user(
            user_id=current_user.id,
            user_data=user_data,
            updated_by=current_user.id
        )
        
        logger.info("User updated own profile", user_id=current_user.id)
        return updated_user
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    except Exception as e:
        logger.error("Error updating user profile", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/me/student-profile",
    response_model=StudentProfileResponse,
    summary="Мой профиль студента",
    description="Получение дополнительной информации профиля студента",
    responses={
        200: {"description": "Профиль студента"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
        404: {"description": "Профиль студента не найден"},
    }
)
async def get_my_student_profile(
    current_user: User = Depends(get_current_active_user),
    student_service: UserService = Depends(get_student_profile_service)
) -> StudentProfileResponse:
    """Получение своего профиля студента."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для студентов"
        )
    
    try:
        profile = await student_service.get_student_profile(current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль студента не найден"
            )
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting student profile", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/me/student-profile",
    response_model=StudentProfileResponse,
    summary="Обновление профиля студента",
    description="Обновление дополнительной информации профиля студента",
    responses={
        200: {"description": "Профиль студента обновлен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_my_student_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    student_service: UserService = Depends(get_student_profile_service)
) -> StudentProfileResponse:
    """Обновление своего профиля студента."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для студентов"
        )
    
    try:
        updated_profile = await student_service.update_student_profile(
            user_id=current_user.id,
            profile_data=profile_data
        )
        
        logger.info("Student updated own profile", user_id=current_user.id)
        return updated_profile
    
    except Exception as e:
        logger.error("Error updating student profile", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/me/avatar",
    summary="Загрузить аватар",
    description="Загрузка аватара для текущего пользователя (студент или ментор)",
    responses={
        200: {"description": "Аватар успешно загружен"},
        400: {"description": "Некорректный файл"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов и менторов"},
    }
)
async def upload_avatar(
    file: UploadFile = File(..., description="Файл аватара (JPG, PNG)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Загрузка аватара для текущего пользователя."""
    
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Администраторы не могут загружать аватары"
        )
    
    try:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не выбран"
            )
        
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
            )
        
        max_size = 5 * 1024 * 1024
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла превышает 5MB"
            )
        
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        unique_filename = f"{uuid4().hex}{file_extension}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        file_url = f"/uploads/avatars/{unique_filename}"
        
        if current_user.role == UserRole.STUDENT:
            from modules.users.domain.models import Student
            student_query = select(Student).where(Student.user_id == current_user.id)
            student_result = await db.execute(student_query)
            student = student_result.scalar_one_or_none()
            
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Профиль студента не найден"
                )
            
            old_avatar_url = student.avatar_url
            student.avatar_url = file_url
            await db.commit()
            
            if old_avatar_url and old_avatar_url.startswith("/uploads/avatars/"):
                old_file_path = Path(old_avatar_url.lstrip("/"))
                if old_file_path.exists():
                    try:
                        old_file_path.unlink()
                    except Exception as e:
                        logger.warning("Failed to delete old avatar", old_path=str(old_file_path), error=str(e))
            
            logger.info("Student avatar uploaded", user_id=current_user.id, avatar_url=file_url)
            return {"avatar_url": file_url, "message": "Аватар успешно загружен"}
        
        elif current_user.role == UserRole.MENTOR:
            from modules.mentors.domain.models import Mentor
            mentor_query = select(Mentor).where(Mentor.user_id == current_user.id)
            mentor_result = await db.execute(mentor_query)
            mentor = mentor_result.scalar_one_or_none()
            
            if not mentor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Профиль ментора не найден"
                )
            
            old_avatar_url = mentor.avatar_url
            mentor.avatar_url = file_url
            await db.commit()
            
            if old_avatar_url and old_avatar_url.startswith("/uploads/avatars/"):
                old_file_path = Path(old_avatar_url.lstrip("/"))
                if old_file_path.exists():
                    try:
                        old_file_path.unlink()
                    except Exception as e:
                        logger.warning("Failed to delete old avatar", old_path=str(old_file_path), error=str(e))
            
            logger.info("Mentor avatar uploaded", user_id=current_user.id, avatar_url=file_url)
            return {"avatar_url": file_url, "message": "Аватар успешно загружен"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading avatar", user_id=current_user.id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при загрузке аватара"
        )


# Администраторские endpoints

@router.get(
    "",
    response_model=UserList,
    summary="Список пользователей",
    description="Получение списка пользователей с фильтрацией (только для администраторов)",
    responses={
        200: {"description": "Список пользователей"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_users_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    role: Optional[UserRole] = Query(None, description="Фильтр по роли"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    search: Optional[str] = Query(None, description="Поиск по имени или email"),
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
) -> UserList:
    """Получение списка пользователей (только для администраторов)."""
    try:
        users, total = await user_service.get_users_list(
            page=page,
            page_size=page_size,
            role=role,
            is_active=is_active,
            search_query=search
        )
        
        return UserList(
            users=users,
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error("Error getting users list", error=str(e), admin_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "",
    response_model=UserWithProfile,
    status_code=status.HTTP_201_CREATED,
    summary="Создание пользователя",
    description="Создание нового пользователя (только для администраторов)",
    responses={
        201: {"description": "Пользователь создан"},
        400: {"description": "Пользователь с таким email уже существует"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
) -> UserWithProfile:
    """Создание нового пользователя (только для администраторов)."""
    try:
        new_user = await user_service.create_user(
            user_data=user_data,
            created_by=current_user.id
        )
        
        logger.info("User created by admin", user_id=new_user.id, admin_id=current_user.id)
        return new_user
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error creating user", error=str(e), admin_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/{user_id}",
    response_model=UserWithProfile,
    summary="Информация о пользователе",
    description="Получение информации о конкретном пользователе",
    responses={
        200: {"description": "Информация о пользователе"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пользователь не найден"},
    }
)
async def get_user_by_id(
    user_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    user_service: UserService = Depends(get_user_service)
) -> UserWithProfile:
    """Получение информации о пользователе."""
    # Проверяем права доступа
    if not (current_user_info.is_admin or current_user_info.can_access_resource(user_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    
    user = await user_service.get_user_by_id(user_id, include_profile=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.put(
    "/{user_id}",
    response_model=UserWithProfile,
    summary="Обновление пользователя",
    description="Обновление информации о пользователе (только для администраторов)",
    responses={
        200: {"description": "Пользователь обновлен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пользователь не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_user_by_id(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
) -> UserWithProfile:
    """Обновление пользователя (только для администраторов)."""
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            user_data=user_data,
            updated_by=current_user.id
        )
        
        logger.info("User updated by admin", user_id=user_id, admin_id=current_user.id)
        return updated_user
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    except Exception as e:
        logger.error("Error updating user", user_id=user_id, error=str(e), admin_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.patch(
    "/{user_id}/activation",
    response_model=UserWithProfile,
    summary="Изменение активности пользователя",
    description="Активация или деактивация пользователя (только для администраторов)",
    responses={
        200: {"description": "Статус пользователя изменен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Пользователь не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def change_user_activation(
    user_id: UUID,
    activation_data: UserActivation,
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
) -> UserWithProfile:
    """Изменение активности пользователя (только для администраторов)."""
    try:
        if activation_data.is_active:
            updated_user = await user_service.activate_user(
                user_id=user_id,
                activated_by=current_user.id
            )
        else:
            updated_user = await user_service.deactivate_user(
                user_id=user_id,
                reason=activation_data.reason,
                deactivated_by=current_user.id
            )
        
        action = "activated" if activation_data.is_active else "deactivated"
        logger.info(f"User {action} by admin", user_id=user_id, admin_id=current_user.id)
        
        return updated_user
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    except Exception as e:
        logger.error("Error changing user activation", user_id=user_id, error=str(e), admin_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/stats/overview",
    response_model=UserStatsOverview,
    summary="Статистика пользователей",
    description="Получение статистики пользователей (только для администраторов)",
    responses={
        200: {"description": "Статистика пользователей"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_users_stats(
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service)
) -> UserStatsOverview:
    """Получение статистики пользователей (только для администраторов)."""
    try:
        stats = await user_service.get_user_stats()
        return stats
    
    except Exception as e:
        logger.error("Error getting user stats", error=str(e), admin_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности модуля пользователей",
    description="Endpoint для проверки работоспособности модуля пользователей",
    responses={
        200: {"description": "Модуль работает корректно"},
    }
)
async def users_health_check() -> Dict[str, Any]:
    """Проверка работоспособности модуля пользователей."""
    return {
        "status": "healthy",
        "module": "users",
        "timestamp": "2024-09-10T18:00:00Z",
        "features": [
            "user_management",
            "profile_management",
            "student_profiles",
            "user_statistics",
            "role_based_access"
        ]
    }

