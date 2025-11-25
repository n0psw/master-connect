"""
API роуты для модуля менторов.
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_active_user,
    get_current_admin,
    get_current_mentor,
    get_current_user_info,
    CurrentUserInfo,
)
from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from db.session import get_db
from modules.mentors.application.services import MentorService, MentorUniversityService
from modules.mentors.domain.schemas import (
    AdminMentorCreate,
    AdminMentorDetail,
    AdminMentorUpdate,
    MentorCard,
    MentorCreate,
    MentorDetail,
    MentorFilters,
    MentorList,
    MentorResponse,
    MentorSortOptions,
    MentorStats,
    MentorUniversityCreate,
    MentorUniversityResponse,
    MentorUniversityUpdate,
    MentorUpdate,
    PopularLanguages,
    PopularSubjects,
    UniversitySuggestion,
)
from modules.users.domain.models import User, UserRole

logger = get_logger(__name__)

router = APIRouter(prefix="/mentors", tags=["Менторы"])


async def get_mentor_service(db: AsyncSession = Depends(get_db)) -> MentorService:
    """Dependency для получения сервиса менторов."""
    return MentorService(db)


async def get_mentor_university_service(db: AsyncSession = Depends(get_db)) -> MentorUniversityService:
    """Dependency для получения сервиса образования менторов."""
    return MentorUniversityService(db)


# === Публичные endpoints для каталога ===

@router.get(
    "",
    response_model=MentorList,
    summary="Каталог менторов",
    description="Получение списка менторов с фильтрацией и сортировкой",
    responses={
        200: {"description": "Список менторов"},
        400: {"description": "Некорректные параметры запроса"},
        422: {"description": "Ошибка валидации"},
    }
)
async def get_mentors_catalog(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    sort: MentorSortOptions = Query(MentorSortOptions.RATING_DESC, description="Сортировка"),
    languages: Optional[List[str]] = Query(None, description="Фильтр по языкам"),
    subjects: Optional[List[str]] = Query(None, description="Фильтр по предметам"),
    countries: Optional[List[str]] = Query(None, description="Фильтр по странам"),
    price_min: Optional[Decimal] = Query(None, ge=0, description="Минимальная цена"),
    price_max: Optional[Decimal] = Query(None, ge=0, description="Максимальная цена"),
    rating_min: Optional[Decimal] = Query(None, ge=0, le=5, description="Минимальный рейтинг"),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> MentorList:
    """
    Получение каталога менторов.
    
    Поддерживает фильтрацию по различным критериям и сортировку.
    """
    try:
        # Создаем фильтры
        filters = MentorFilters(
            languages=languages,
            subjects=subjects,
            countries=countries,
            price_min=price_min,
            price_max=price_max,
            rating_min=rating_min,
        )
        
        mentors, total = await mentor_service.get_mentors_catalog(
            page=page,
            page_size=page_size,
            filters=filters,
            sort=sort,
            search_query=search
        )
        
        return MentorList(
            mentors=mentors,
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error("Error getting mentors catalog", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/{mentor_id}",
    response_model=MentorDetail,
    summary="Детали ментора",
    description="Получение детальной информации о менторе",
    responses={
        200: {"description": "Информация о менторе"},
        404: {"description": "Ментор не найден"},
    }
)
async def get_mentor_detail(
    mentor_id: UUID,
    mentor_service: MentorService = Depends(get_mentor_service)
) -> MentorDetail:
    """Получение детальной информации о менторе."""
    try:
        mentor_detail = await mentor_service.get_mentor_detail(mentor_id)
        
        if not mentor_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ментор не найден"
            )
        
        return mentor_detail
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error("Error getting mentor detail", mentor_id=mentor_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Endpoints для менторов ===

@router.get(
    "/me/profile",
    response_model=MentorResponse,
    summary="Мой профиль ментора",
    description="Получение профиля текущего ментора",
    responses={
        200: {"description": "Профиль ментора"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Профиль ментора не найден"},
    }
)
async def get_my_mentor_profile(
    current_user: User = Depends(get_current_mentor),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> MentorResponse:
    """Получение профиля текущего ментора."""
    try:
        mentor_detail = await mentor_service.get_mentor_detail(current_user.id)
        
        if not mentor_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль ментора не найден"
            )
        
        return mentor_detail.mentor
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error("Error getting mentor profile", mentor_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/me/profile",
    response_model=MentorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать профиль ментора",
    description="Создание профиля ментора для текущего пользователя",
    responses={
        201: {"description": "Профиль ментора создан"},
        400: {"description": "Профиль уже существует или некорректные данные"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_my_mentor_profile(
    mentor_data: MentorCreate,
    current_user: User = Depends(get_current_mentor),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> MentorResponse:
    """Создание профиля ментора."""
    try:
        mentor = await mentor_service.create_mentor_profile(
            user_id=current_user.id,
            mentor_data=mentor_data,
            created_by=current_user.id
        )
        
        logger.info("Mentor profile created", mentor_id=current_user.id)
        return mentor
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error creating mentor profile", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/me/profile",
    response_model=MentorResponse,
    summary="Обновить профиль ментора",
    description="Обновление профиля текущего ментора",
    responses={
        200: {"description": "Профиль ментора обновлен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Профиль ментора не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_my_mentor_profile(
    mentor_data: MentorUpdate,
    current_user: User = Depends(get_current_mentor),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> MentorResponse:
    """Обновление профиля ментора."""
    try:
        mentor = await mentor_service.update_mentor_profile(
            mentor_id=current_user.id,
            mentor_data=mentor_data,
            updated_by=current_user.id
        )
        
        logger.info("Mentor profile updated", mentor_id=current_user.id)
        return mentor
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль ментора не найден"
        )
    
    except Exception as e:
        logger.error("Error updating mentor profile", mentor_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Управление образованием ===

@router.post(
    "/me/universities",
    response_model=MentorUniversityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить образование",
    description="Добавление записи об образовании в профиль ментора",
    responses={
        201: {"description": "Образование добавлено"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Ментор не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def add_my_university(
    university_data: MentorUniversityCreate,
    current_user: User = Depends(get_current_mentor),
    university_service: MentorUniversityService = Depends(get_mentor_university_service)
) -> MentorUniversityResponse:
    """Добавление образования к профилю ментора."""
    try:
        university = await university_service.add_university(
            mentor_id=current_user.id,
            university_data=university_data
        )
        
        logger.info("University added to mentor", mentor_id=current_user.id, university_id=university.id)
        return university
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ментор не найден"
        )
    
    except Exception as e:
        logger.error("Error adding university", mentor_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/me/universities/{university_id}",
    response_model=MentorUniversityResponse,
    summary="Обновить образование",
    description="Обновление записи об образовании",
    responses={
        200: {"description": "Образование обновлено"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Образование не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_my_university(
    university_id: UUID,
    university_data: MentorUniversityUpdate,
    current_user: User = Depends(get_current_mentor),
    university_service: MentorUniversityService = Depends(get_mentor_university_service)
) -> MentorUniversityResponse:
    """Обновление образования ментора."""
    try:
        # TODO: Добавить проверку прав доступа к записи об образовании
        university = await university_service.update_university(
            university_id=university_id,
            university_data=university_data
        )
        
        logger.info("University updated", mentor_id=current_user.id, university_id=university_id)
        return university
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Образование не найдено"
        )
    
    except Exception as e:
        logger.error("Error updating university", university_id=university_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete(
    "/me/universities/{university_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить образование",
    description="Удаление записи об образовании",
    responses={
        204: {"description": "Образование удалено"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Образование не найдено"},
    }
)
async def delete_my_university(
    university_id: UUID,
    current_user: User = Depends(get_current_mentor),
    university_service: MentorUniversityService = Depends(get_mentor_university_service)
) -> None:
    """Удаление образования ментора."""
    try:
        # TODO: Добавить проверку прав доступа к записи об образовании
        deleted = await university_service.delete_university(university_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Образование не найдено"
            )
        
        logger.info("University deleted", mentor_id=current_user.id, university_id=university_id)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error("Error deleting university", university_id=university_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Административные endpoints ===

@router.post(
    "/admin",
    response_model=AdminMentorDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создать ментора",
    description="Создание нового ментора администратором",
    responses={
        201: {"description": "Ментор создан"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_mentor_admin(
    mentor_data: AdminMentorCreate,
    current_user: User = Depends(get_current_admin),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> AdminMentorDetail:
    """Создание ментора администратором."""
    try:
        mentor = await mentor_service.create_mentor_as_admin(
            mentor_data=mentor_data,
            created_by=current_user.id
        )
        
        logger.info("Mentor created by admin", mentor_id=mentor.mentor.user_id, admin_id=current_user.id)
        return mentor
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error creating mentor", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/admin/{mentor_id}",
    response_model=AdminMentorDetail,
    summary="Получить ментора (админ)",
    description="Получение детальной информации о менторе для администратора",
    responses={
        200: {"description": "Информация о менторе"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Ментор не найден"},
    }
)
async def get_mentor_admin(
    mentor_id: UUID,
    current_user: User = Depends(get_current_admin),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> AdminMentorDetail:
    """Получение детальной информации о менторе для администратора."""
    try:
        mentor = await mentor_service.get_admin_mentor_detail(mentor_id)
        return mentor
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ментор не найден"
        )
    
    except Exception as e:
        logger.error("Error getting mentor", mentor_id=mentor_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/admin/{mentor_id}",
    response_model=AdminMentorDetail,
    summary="Обновить ментора",
    description="Обновление информации о менторе администратором",
    responses={
        200: {"description": "Ментор обновлен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Ментор не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_mentor_admin(
    mentor_id: UUID,
    mentor_data: AdminMentorUpdate,
    current_user: User = Depends(get_current_admin),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> AdminMentorDetail:
    """Обновление ментора администратором."""
    try:
        mentor = await mentor_service.update_mentor_as_admin(
            mentor_id=mentor_id,
            mentor_data=mentor_data,
            updated_by=current_user.id
        )
        
        logger.info("Mentor updated by admin", mentor_id=mentor_id, admin_id=current_user.id)
        return mentor
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ментор не найден"
        )
    
    except Exception as e:
        logger.error("Error updating mentor", mentor_id=mentor_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete(
    "/admin/{mentor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ментора",
    description="Удаление ментора администратором",
    responses={
        204: {"description": "Ментор удален"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Ментор не найден"},
    }
)
async def delete_mentor_admin(
    mentor_id: UUID,
    current_user: User = Depends(get_current_admin),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> None:
    """Удаление ментора администратором."""
    try:
        await mentor_service.delete_mentor_as_admin(
            mentor_id=mentor_id,
            deleted_by=current_user.id
        )
        
        logger.info("Mentor deleted by admin", mentor_id=mentor_id, admin_id=current_user.id)
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ментор не найден"
        )
    
    except Exception as e:
        logger.error("Error deleting mentor", mentor_id=mentor_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/stats/overview",
    response_model=MentorStats,
    summary="Статистика менторов",
    description="Получение статистики менторов (только для администраторов)",
    responses={
        200: {"description": "Статистика менторов"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_mentors_stats(
    current_user: User = Depends(get_current_admin),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> MentorStats:
    """Получение статистики менторов (только для администраторов)."""
    try:
        stats = await mentor_service.get_mentor_stats()
        return stats
    
    except Exception as e:
        logger.error("Error getting mentor stats", error=str(e), admin_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Утилитарные endpoints ===

@router.get(
    "/suggestions/subjects",
    response_model=PopularSubjects,
    summary="Популярные предметы",
    description="Получение списка популярных предметов среди менторов",
    responses={
        200: {"description": "Популярные предметы"},
    }
)
async def get_popular_subjects(
    limit: int = Query(20, ge=1, le=100, description="Количество предметов"),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> PopularSubjects:
    """Получение популярных предметов."""
    try:
        subjects = await mentor_service.get_popular_subjects(limit)
        return subjects
    
    except Exception as e:
        logger.error("Error getting popular subjects", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/suggestions/languages",
    response_model=PopularLanguages,
    summary="Популярные языки",
    description="Получение списка популярных языков консультаций",
    responses={
        200: {"description": "Популярные языки"},
    }
)
async def get_popular_languages(
    limit: int = Query(10, ge=1, le=50, description="Количество языков"),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> PopularLanguages:
    """Получение популярных языков."""
    try:
        languages = await mentor_service.get_popular_languages(limit)
        return languages
    
    except Exception as e:
        logger.error("Error getting popular languages", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/suggestions/universities",
    response_model=List[UniversitySuggestion],
    summary="Предложения университетов",
    description="Поиск университетов для автокомплита",
    responses={
        200: {"description": "Предложения университетов"},
    }
)
async def get_university_suggestions(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=50, description="Количество предложений"),
    mentor_service: MentorService = Depends(get_mentor_service)
) -> List[UniversitySuggestion]:
    """Получение предложений университетов для автокомплита."""
    try:
        suggestions = await mentor_service.get_university_suggestions(
            query=q,
            limit=limit
        )
        return suggestions
    
    except Exception as e:
        logger.error("Error getting university suggestions", query=q, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности модуля менторов",
    description="Endpoint для проверки работоспособности модуля менторов",
    responses={
        200: {"description": "Модуль работает корректно"},
    }
)
async def mentors_health_check() -> Dict[str, Any]:
    """Проверка работоспособности модуля менторов."""
    return {
        "status": "healthy",
        "module": "mentors",
        "timestamp": "2024-09-10T18:00:00Z",
        "features": [
            "mentor_catalog",
            "mentor_profiles",
            "mentor_verification",
            "university_management",
            "mentor_statistics",
            "search_and_filtering",
            "autocomplete_suggestions"
        ]
    }

