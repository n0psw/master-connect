"""
API роуты для модуля бронирований.
"""
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_active_user,
    get_current_admin,
    get_current_student,
    get_current_mentor,
    get_current_user_info,
    CurrentUserInfo,
)
from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from db.session import get_db
from modules.bookings.application.services import BookingModerationService, BookingService
from modules.bookings.domain.models import BookingStatus, Booking
from modules.bookings.domain.schemas import (
    BookingCancellationRequest,
    BookingCreate,
    BookingDetail,
    BookingFilters,
    BookingList,
    BookingModerationQueue,
    BookingPaymentConfirmation,
    BookingRescheduleRequest,
    BookingResponse,
    BookingStats,
)
from modules.users.domain.models import User, UserRole

logger = get_logger(__name__)

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


async def get_booking_service(db: AsyncSession = Depends(get_db)) -> BookingService:
    """Dependency для получения сервиса бронирований."""
    return BookingService(db)


async def get_moderation_service(db: AsyncSession = Depends(get_db)) -> BookingModerationService:
    """Dependency для получения сервиса модерации."""
    return BookingModerationService(db)


# === Endpoints для студентов ===

@router.post(
    "",
    response_model=BookingResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Создать бронирование",
    description="Создание нового бронирования консультации (только для студентов)",
    responses={
        201: {"description": "Бронирование создано"},
        400: {"description": "Некорректные данные или слот недоступен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
        404: {"description": "Ментор не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_student),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """
    Создание нового бронирования консультации.
    
    После создания бронирование получает статус HOLD и студенту дается время
    для совершения оплаты.
    """
    try:
        booking = await booking_service.create_booking(
            student_id=current_user.id,
            booking_data=booking_data
        )
        
        logger.info("Booking created by student", student_id=current_user.id, booking_id=booking.id)
        return booking
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        user_id = str(current_user.id) if hasattr(current_user, 'id') else 'unknown'
        logger.error("Error creating booking", student_id=user_id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/mark-payment",
    response_model=BookingResponse,
    summary="Отметить оплату",
    description="Отметка студентом о совершении оплаты ('Я оплатил')",
    responses={
        200: {"description": "Оплата отмечена, бронирование ожидает подтверждения"},
        400: {"description": "Нельзя отметить оплату для данного бронирования"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для студентов"},
        404: {"description": "Бронирование не найдено"},
    }
)
async def mark_payment(
    booking_id: UUID,
    current_user: User = Depends(get_current_student),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """
    Отметка студентом о совершении оплаты.
    
    Переводит бронирование в статус AWAITING_VERIFICATION для проверки администратором.
    """
    try:
        booking = await booking_service.mark_payment_by_student(
            booking_id=booking_id,
            student_id=current_user.id
        )
        
        logger.info("Payment marked", student_id=current_user.id, booking_id=booking_id)
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except (BusinessLogicError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error marking payment", booking_id=booking_id, student_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Общие endpoints (для студентов и менторов) ===

@router.get(
    "/my",
    response_model=BookingList,
    summary="Мои бронирования",
    description="Получение списка бронирований текущего пользователя",
    responses={
        200: {"description": "Список бронирований"},
        401: {"description": "Требуется авторизация"},
    }
)
async def get_my_bookings(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    statuses: Optional[List[BookingStatus]] = Query(None, description="Фильтр по статусам"),
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingList:
    """Получение списка бронирований текущего пользователя."""
    try:
        # Создаем фильтры
        filters = BookingFilters(status=statuses) if statuses else None
        
        bookings = await booking_service.get_bookings_list(
            user_id=current_user_info.id,
            user_role=current_user_info.role,
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        return bookings
    
    except Exception as e:
        logger.error("Error getting user bookings", user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/{booking_id}",
    response_model=BookingDetail,
    summary="Детали бронирования",
    description="Получение детальной информации о бронировании",
    responses={
        200: {"description": "Детали бронирования"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
    }
)
async def get_booking_detail(
    booking_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingDetail:
    """Получение детальной информации о бронировании."""
    try:
        booking_detail = await booking_service.get_booking_detail(
            booking_id=booking_id,
            user_id=current_user_info.id,
            user_role=current_user_info.role
        )
        
        return booking_detail
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except PermissionDeniedError:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для доступа к бронированию"
        )
    
    except Exception as e:
        logger.error("Error getting booking detail", booking_id=booking_id, user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    summary="Отменить бронирование",
    description="Отмена бронирования пользователем",
    responses={
        200: {"description": "Бронирование отменено"},
        400: {"description": "Нельзя отменить данное бронирование"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def cancel_booking(
    booking_id: UUID,
    cancellation_data: BookingCancellationRequest,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """Отмена бронирования пользователем."""
    try:
        booking = await booking_service.cancel_booking(
            booking_id=booking_id,
            user_id=current_user_info.id,
            user_role=current_user_info.role,
            cancellation_data=cancellation_data
        )
        
        logger.info("Booking cancelled by user", user_id=current_user_info.id, booking_id=booking_id)
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except (BusinessLogicError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error cancelling booking", booking_id=booking_id, user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/reschedule",
    response_model=BookingResponse,
    summary="Перенести бронирование",
    description="Перенос бронирования на другое время",
    responses={
        200: {"description": "Бронирование перенесено"},
        400: {"description": "Нельзя перенести данное бронирование или новый слот недоступен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def reschedule_booking(
    booking_id: UUID,
    reschedule_data: BookingRescheduleRequest,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """Перенос бронирования на другое время."""
    try:
        booking = await booking_service.reschedule_booking(
            booking_id=booking_id,
            user_id=current_user_info.id,
            user_role=current_user_info.role,
            reschedule_data=reschedule_data
        )
        
        logger.info("Booking rescheduled by user", user_id=current_user_info.id, booking_id=booking_id)
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except (BusinessLogicError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error rescheduling booking", booking_id=booking_id, user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/my/stats",
    response_model=BookingStats,
    summary="Моя статистика бронирований",
    description="Получение статистики бронирований текущего пользователя",
    responses={
        200: {"description": "Статистика бронирований"},
        401: {"description": "Требуется авторизация"},
    }
)
async def get_my_booking_stats(
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingStats:
    """Получение статистики бронирований текущего пользователя."""
    try:
        stats = await booking_service.get_booking_stats(
            user_id=current_user_info.id,
            user_role=current_user_info.role
        )
        
        return stats
    
    except Exception as e:
        logger.error("Error getting booking stats", user_id=current_user_info.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Административные endpoints ===

@router.get(
    "/admin/queue",
    response_model=BookingModerationQueue,
    summary="Очередь модерации",
    description="Получение очереди бронирований для модерации (только для администраторов)",
    responses={
        200: {"description": "Очередь модерации"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_moderation_queue(
    current_user: User = Depends(get_current_admin),
    moderation_service: BookingModerationService = Depends(get_moderation_service)
) -> BookingModerationQueue:
    """Получение очереди модерации бронирований (только для администраторов)."""
    try:
        queue = await moderation_service.get_moderation_queue()
        return queue
    
    except Exception as e:
        logger.error("Error getting moderation queue", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/admin/confirm-payment",
    response_model=BookingResponse,
    summary="Подтвердить оплату",
    description="Подтверждение или отклонение оплаты администратором",
    responses={
        200: {"description": "Оплата обработана"},
        400: {"description": "Нельзя обработать оплату для данного бронирования"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def confirm_payment(
    booking_id: UUID,
    confirmation_data: BookingPaymentConfirmation,
    current_user: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """Подтверждение или отклонение оплаты администратором."""
    try:
        booking = await booking_service.confirm_payment_by_admin(
            booking_id=booking_id,
            admin_id=current_user.id,
            confirmation_data=confirmation_data
        )
        
        action = "confirmed" if confirmation_data.payment_confirmed else "rejected"
        logger.info(f"Payment {action} by admin", admin_id=current_user.id, booking_id=booking_id)
        
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error confirming payment", booking_id=booking_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/admin/all",
    response_model=BookingList,
    summary="Все бронирования",
    description="Получение списка всех бронирований (только для администраторов)",
    responses={
        200: {"description": "Список всех бронирований"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_all_bookings(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    status: Optional[List[BookingStatus]] = Query(None, description="Фильтр по статусам"),
    mentor_id: Optional[UUID] = Query(None, description="Фильтр по ментору"),
    student_id: Optional[UUID] = Query(None, description="Фильтр по студенту"),
    date_from: Optional[date] = Query(None, description="Дата начала периода (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Дата окончания периода (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Поиск по имени студента/ментора или email"),
    sort: Optional[str] = Query("created_desc", description="Сортировка: created_desc, created_asc, scheduled_desc, scheduled_asc, price_desc, price_asc"),
    current_user: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingList:
    """Получение списка всех бронирований (только для администраторов)."""
    try:
        # Преобразуем date в datetime для фильтров
        date_from_dt = None
        date_to_dt = None
        if date_from:
            date_from_dt = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
        if date_to:
            date_to_dt = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Создаем фильтры
        filters = BookingFilters(
            status=status,
            mentor_id=mentor_id,
            student_id=student_id,
            date_from=date_from_dt,
            date_to=date_to_dt,
            search=search
        )
        
        bookings = await booking_service.get_bookings_list(
            user_id=current_user.id,
            user_role=UserRole.ADMIN,
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort
        )
        
        return bookings
    
    except Exception as e:
        logger.error("Error getting all bookings", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/admin/mark-completed",
    response_model=BookingResponse,
    summary="Отметить как завершенное",
    description="Отметить бронирование как завершенное (только для администраторов)",
    responses={
        200: {"description": "Бронирование отмечено как завершенное"},
        400: {"description": "Нельзя завершить данное бронирование"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
    }
)
async def mark_booking_completed(
    booking_id: UUID,
    current_user: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """Отметить бронирование как завершенное."""
    try:
        booking = await booking_service.mark_booking_completed(
            booking_id=booking_id,
            admin_id=current_user.id,
            user_role=current_user.role
        )
        
        logger.info("Booking marked as completed by admin", admin_id=current_user.id, booking_id=booking_id)
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error marking booking as completed", booking_id=booking_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/mentor/mark-completed",
    response_model=BookingResponse,
    summary="Завершить консультацию",
    description="Отметить консультацию как завершенную (для ментора)",
    responses={
        200: {"description": "Консультация отмечена как завершенная"},
        400: {"description": "Нельзя завершить данную консультацию"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
    }
)
async def mark_booking_completed_by_mentor(
    booking_id: UUID,
    current_user: User = Depends(get_current_mentor),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """Отметить консультацию как завершенную ментором."""
    try:
        booking = await booking_service.mark_booking_completed_by_mentor(
            booking_id=booking_id,
            mentor_id=current_user.id
        )
        
        logger.info("Booking marked as completed by mentor", mentor_id=current_user.id, booking_id=booking_id)
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except (BusinessLogicError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error marking booking as completed by mentor", booking_id=booking_id, mentor_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/{booking_id}/admin/mark-no-show",
    response_model=BookingResponse,
    summary="Отметить как неявку",
    description="Отметить бронирование как неявку (только для администраторов)",
    responses={
        200: {"description": "Бронирование отмечено как неявка"},
        400: {"description": "Нельзя отметить неявку для данного бронирования"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
    }
)
async def mark_booking_no_show(
    booking_id: UUID,
    no_show_type: str = Query("student", description="Тип неявки: student или mentor"),
    current_user: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingResponse:
    """Отметить бронирование как неявку."""
    try:
        booking = await booking_service.mark_booking_no_show(
            booking_id=booking_id,
            admin_id=current_user.id,
            user_role=current_user.role,
            no_show_type=no_show_type
        )
        
        logger.info("Booking marked as no show by admin", admin_id=current_user.id, booking_id=booking_id, no_show_type=no_show_type)
        return booking
    
    except NotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error marking booking as no show", booking_id=booking_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/admin/stats",
    response_model=BookingStats,
    summary="Общая статистика бронирований",
    description="Получение общей статистики бронирований (только для администраторов)",
    responses={
        200: {"description": "Статистика бронирований"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_all_booking_stats(
    current_user: User = Depends(get_current_admin),
    booking_service: BookingService = Depends(get_booking_service)
) -> BookingStats:
    """Получение общей статистики бронирований (только для администраторов)."""
    try:
        stats = await booking_service.get_booking_stats()
        return stats
    
    except Exception as e:
        logger.error("Error getting all booking stats", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )




@router.get(
    "/health",
    summary="Проверка работоспособности модуля бронирований",
    description="Endpoint для проверки работоспособности модуля бронирований",
    responses={
        200: {"description": "Модуль работает корректно"},
    }
)
async def bookings_health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Проверка работоспособности модуля бронирований."""
    from datetime import datetime, timezone
    
    try:
        # Проверяем подключение к БД
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "module": "bookings",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "features": [
            "booking_creation",
            "payment_marking",
            "payment_confirmation",
            "booking_cancellation",
            "booking_rescheduling",
            "moderation_queue",
            "booking_statistics",
            "state_machine",
            "calendar_integration",
            "admin_management"
        ]
    }

