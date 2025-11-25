"""
API роуты для модуля отзывов.
"""
from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_active_user,
    get_current_admin,
    get_current_student,
    get_current_user_info,
    CurrentUserInfo,
)
from modules.users.domain.models import User
from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from db.session import get_db
from modules.reviews.application.services import ReviewService
from modules.reviews.domain.schemas import (
    ReviewCreate,
    ReviewList,
    ReviewResponse,
    ReviewStats,
    ReviewUpdate,
)
from modules.users.domain.models import UserRole, Student

logger = get_logger(__name__)

router = APIRouter(prefix="/reviews", tags=["Отзывы"])


async def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    """Dependency для получения сервиса отзывов."""
    logger.debug("get_review_service called")
    return ReviewService(db)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отзыв",
    description="Создание отзыва на завершенную консультацию (только для студентов)",
    responses={
        201: {"description": "Отзыв создан"},
        400: {"description": "Некорректные данные или консультация не завершена"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
        404: {"description": "Бронирование не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_review(
    review_data: ReviewCreate,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    review_service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    """Создание отзыва на завершенную консультацию."""
    if current_user_info.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут оставлять отзывы"
        )
    
    try:
        # Получаем student_id из таблицы Student по user_id
        student_query = select(Student).where(Student.user_id == current_user_info.id)
        student_result = await db.execute(student_query)
        student_obj = student_result.scalar_one_or_none()
        
        if not student_obj:
            raise NotFoundError("Профиль студента не найден")
        
        logger.info(
            "Creating review",
            user_id=current_user_info.id,
            student_id=student_obj.user_id,
            booking_id=review_data.booking_id
        )
        
        review = await review_service.create_review(
            review_data=review_data,
            student_id=student_obj.user_id
        )
        
        logger.info("Review created", review_id=review.id, student_id=student_obj.user_id)
        
        return review
    
    except NotFoundError as e:
        logger.error("Not found error creating review", user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except (BusinessLogicError, PermissionDeniedError) as e:
        logger.error("Business logic error creating review", user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error creating review", user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/my",
    summary="Мои отзывы",
    description="Получение отзывов текущего студента",
    responses={
        200: {"description": "Список отзывов"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
    }
)
async def get_my_reviews(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    review_service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Получение отзывов текущего студента."""
    logger.info(
        "get_my_reviews START",
        page=page,
        page_size=page_size,
        user_id=str(current_user_info.id) if current_user_info else None,
        role=str(current_user_info.role) if current_user_info else None
    )
    
    if current_user_info.role != UserRole.STUDENT:
        logger.warning("Access denied - not a student", user_id=current_user_info.id, role=current_user_info.role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для студентов"
        )
    
    try:
        logger.debug("Looking up student profile", user_id=current_user_info.id)
        student_query = select(Student).where(Student.user_id == current_user_info.id)
        student_result = await db.execute(student_query)
        student_obj = student_result.scalar_one_or_none()
        
        if not student_obj:
            logger.warning("Student profile not found, returning empty list", user_id=current_user_info.id)
            return {
                "reviews": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        logger.info(
            "Getting reviews for student",
            user_id=current_user_info.id,
            student_id=str(student_obj.user_id),
            page=page,
            page_size=page_size
        )
        
        result = await review_service.get_reviews_by_student(
            student_id=student_obj.user_id,
            page=page,
            page_size=page_size
        )
        
        logger.debug(
            "Reviews query result",
            reviews_count=len(result.get("reviews", [])),
            total=result.get("total", 0),
            result_type=type(result).__name__
        )
        
        logger.info("get_my_reviews SUCCESS", reviews_count=len(result.get("reviews", [])))
        return result
    
    except Exception as e:
        logger.error("Error getting my reviews", user_id=current_user_info.id, error=str(e), exc_info=True)
        return {
            "reviews": [],
            "total": 0,
            "page": page,
            "page_size": page_size
        }


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Получить отзыв",
    description="Получение отзыва по ID",
    responses={
        200: {"description": "Отзыв"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Отзыв не найден"},
    }
)
async def get_review(
    review_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    review_service: ReviewService = Depends(get_review_service)
) -> ReviewResponse:
    """Получение отзыва по ID."""
    try:
        review = await review_service.get_review_by_id(
            review_id=review_id,
            user_id=current_user_info.id,
            user_role=current_user_info.role
        )
        
        return review
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error getting review", review_id=review_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/mentor/{mentor_id}",
    response_model=ReviewList,
    summary="Получить отзывы ментора",
    description="Получение всех отзывов ментора",
    responses={
        200: {"description": "Список отзывов"},
    }
)
async def get_mentor_reviews(
    mentor_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    review_service: ReviewService = Depends(get_review_service)
) -> ReviewList:
    """Получение всех отзывов ментора (публичный endpoint)."""
    try:
        result = await review_service.get_reviews_by_mentor(
            mentor_id=mentor_id,
            page=page,
            page_size=page_size
        )
        
        return ReviewList(**result)
    
    except Exception as e:
        logger.error("Error getting mentor reviews", mentor_id=mentor_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/mentor/{mentor_id}/stats",
    response_model=ReviewStats,
    summary="Получить статистику отзывов ментора",
    description="Получение статистики отзывов ментора",
    responses={
        200: {"description": "Статистика отзывов"},
    }
)
async def get_mentor_review_stats(
    mentor_id: UUID,
    review_service: ReviewService = Depends(get_review_service)
) -> ReviewStats:
    """Получение статистики отзывов ментора (публичный endpoint)."""
    try:
        stats = await review_service.get_mentor_stats(mentor_id=mentor_id)
        return stats
    
    except Exception as e:
        logger.error("Error getting mentor review stats", mentor_id=mentor_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/my",
    summary="Мои отзывы",
    description="Получение отзывов текущего студента",
    responses={
        200: {"description": "Список отзывов"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
    }
)
async def get_my_reviews(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    review_service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Получение отзывов текущего студента."""
    logger.info(
        "get_my_reviews START",
        page=page,
        page_size=page_size,
        user_id=str(current_user_info.id) if current_user_info else None,
        role=str(current_user_info.role) if current_user_info else None
    )
    
    if current_user_info.role != UserRole.STUDENT:
        logger.warning("Access denied - not a student", user_id=current_user_info.id, role=current_user_info.role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только для студентов"
        )
    
    try:
        logger.debug("Looking up student profile", user_id=current_user_info.id)
        student_query = select(Student).where(Student.user_id == current_user_info.id)
        student_result = await db.execute(student_query)
        student_obj = student_result.scalar_one_or_none()
        
        if not student_obj:
            logger.warning("Student profile not found, returning empty list", user_id=current_user_info.id)
            return {
                "reviews": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        logger.info(
            "Getting reviews for student",
            user_id=current_user_info.id,
            student_id=str(student_obj.user_id),
            page=page,
            page_size=page_size
        )
        
        result = await review_service.get_reviews_by_student(
            student_id=student_obj.user_id,
            page=page,
            page_size=page_size
        )
        
        logger.debug(
            "Reviews query result",
            reviews_count=len(result.get("reviews", [])),
            total=result.get("total", 0),
            result_type=type(result).__name__
        )
        
        logger.info("get_my_reviews SUCCESS", reviews_count=len(result.get("reviews", [])))
        return result
    
    except Exception as e:
        logger.error("Error getting my reviews", user_id=current_user_info.id, error=str(e), exc_info=True)
        return {
            "reviews": [],
            "total": 0,
            "page": page,
            "page_size": page_size
        }


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Обновить отзыв",
    description="Обновление своего отзыва",
    responses={
        200: {"description": "Отзыв обновлен"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Отзыв не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_review(
    review_id: UUID,
    update_data: ReviewUpdate,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    review_service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_db)
) -> ReviewResponse:
    """Обновление своего отзыва."""
    if current_user_info.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут редактировать отзывы"
        )
    
    try:
        student_query = select(Student).where(Student.user_id == current_user_info.id)
        student_result = await db.execute(student_query)
        student_obj = student_result.scalar_one_or_none()
        
        if not student_obj:
            raise NotFoundError("Профиль студента не найден")
        
        review = await review_service.update_review(
            review_id=review_id,
            update_data=update_data,
            student_id=student_obj.user_id
        )
        
        logger.info("Review updated", review_id=review_id, student_id=student_obj.user_id)
        
        return review
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error updating review", review_id=review_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить отзыв",
    description="Удаление своего отзыва (студент) или любого отзыва (админ)",
    responses={
        204: {"description": "Отзыв удален"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Отзыв не найден"},
    }
)
async def delete_review(
    review_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    review_service: ReviewService = Depends(get_review_service)
) -> None:
    """Удаление отзыва."""
    try:
        await review_service.delete_review(
            review_id=review_id,
            user_id=current_user_info.id,
            user_role=current_user_info.role
        )
        
        logger.info("Review deleted", review_id=review_id, user_id=current_user_info.id)
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error deleting review", review_id=review_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/admin/recalculate-ratings",
    summary="Пересчитать рейтинги всех менторов",
    description="Пересчитывает рейтинг для всех менторов на основе существующих отзывов (только для админа)",
    responses={
        200: {"description": "Рейтинги успешно пересчитаны"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def recalculate_all_mentor_ratings(
    current_user: "User" = Depends(get_current_admin),
    review_service: ReviewService = Depends(get_review_service)
) -> Dict[str, Any]:
    """Пересчитать рейтинги всех менторов на основе существующих отзывов."""
    try:
        result = await review_service.recalculate_all_mentor_ratings()
        logger.info("All mentor ratings recalculated", updated_count=result.get("updated_count"), total_mentors=result.get("total_mentors"))
        return {
            "message": "Рейтинги успешно пересчитаны",
            "updated_count": result.get("updated_count", 0),
            "total_mentors": result.get("total_mentors", 0)
        }
    except Exception as e:
        logger.error("Error recalculating mentor ratings", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при пересчете рейтингов"
        )

