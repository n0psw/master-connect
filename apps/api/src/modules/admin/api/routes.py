"""
API роуты для административного модуля.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_admin,
    get_current_user_info,
    CurrentUserInfo,
)
from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from db.session import get_db
from modules.admin.application.services import (
    AdminDashboardService,
    AuditLogService,
    SystemManagementService,
    UserManagementService,
)
from modules.admin.domain.schemas import (
    AdminDashboardStats,
    AuditLogFilters,
    AuditLogList,
    BulkOperationResult,
    BookingModerationAction,
    CreateMentorRequest,
    CreateMentorResponse,
    MentorModerationAction,
    ModerationQueue,
    PlatformAnalytics,
    SystemHealth,
    SystemMetrics,
    UserManagementAction,
    UserManagementFilters,
)
from modules.users.domain.models import User
from modules.bookings.domain.models import Booking

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Администрирование"])


# Dependencies
async def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> AdminDashboardService:
    """Dependency для получения сервиса дашборда."""
    return AdminDashboardService(db)


async def get_user_management_service(db: AsyncSession = Depends(get_db)) -> UserManagementService:
    """Dependency для получения сервиса управления пользователями."""
    return UserManagementService(db)


async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditLogService:
    """Dependency для получения сервиса аудит лога."""
    return AuditLogService(db)


async def get_system_service(db: AsyncSession = Depends(get_db)) -> SystemManagementService:
    """Dependency для получения сервиса управления системой."""
    return SystemManagementService(db)


# === Дашборд и аналитика ===

@router.get(
    "/dashboard",
    response_model=AdminDashboardStats,
    summary="Статистика дашборда",
    description="Получение основной статистики для административной панели",
    responses={
        200: {"description": "Статистика дашборда"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    dashboard_service: AdminDashboardService = Depends(get_dashboard_service)
) -> AdminDashboardStats:
    """Получение статистики для административного дашборда."""
    try:
        stats = await dashboard_service.get_dashboard_stats()
        
        logger.info("Dashboard stats retrieved", admin_id=current_user.id)
        return stats
    
    except Exception as e:
        logger.error("Error getting dashboard stats", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/analytics",
    response_model=PlatformAnalytics,
    summary="Аналитика платформы",
    description="Получение детальной аналитики платформы",
    responses={
        200: {"description": "Аналитика платформы"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_platform_analytics(
    period: str = Query("7d", description="Период анализа (7d, 30d, 90d)"),
    current_user: User = Depends(get_current_admin),
    dashboard_service: AdminDashboardService = Depends(get_dashboard_service)
) -> PlatformAnalytics:
    """Получение аналитики платформы."""
    try:
        analytics = await dashboard_service.get_platform_analytics(period)
        
        logger.info("Platform analytics retrieved", admin_id=current_user.id, period=period)
        return analytics
    
    except Exception as e:
        logger.error("Error getting platform analytics", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/moderation/queue",
    response_model=ModerationQueue,
    summary="Очередь модерации",
    description="Получение очереди элементов для модерации",
    responses={
        200: {"description": "Очередь модерации"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_moderation_queue(
    current_user: User = Depends(get_current_admin),
    dashboard_service: AdminDashboardService = Depends(get_dashboard_service)
) -> ModerationQueue:
    """Получение очереди модерации."""
    try:
        queue = await dashboard_service.get_moderation_queue()
        
        logger.info("Moderation queue retrieved", admin_id=current_user.id)
        return queue
    
    except Exception as e:
        logger.error("Error getting moderation queue", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Управление пользователями ===

@router.post(
    "/mentors/create",
    response_model=CreateMentorResponse,
    summary="Создать ментора",
    description="Создание нового ментора администратором",
    responses={
        200: {"description": "Ментор успешно создан"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_mentor(
    mentor_data: CreateMentorRequest,
    current_user: User = Depends(get_current_admin),
    user_service: UserManagementService = Depends(get_user_management_service)
) -> CreateMentorResponse:
    """
    Создание нового ментора администратором.
    
    Создается пользователь с ролью MENTOR и профиль ментора.
    Ментор автоматически верифицируется.
    """
    try:
        result = await user_service.create_mentor(
            mentor_data=mentor_data,
            admin_id=current_user.id
        )
        
        logger.info(
            "Mentor created by admin",
            admin_id=current_user.id,
            mentor_id=result.mentor_id,
            email=result.email
        )
        
        return result
    
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


@router.post(
    "/users/bulk-action",
    response_model=BulkOperationResult,
    summary="Массовое действие над пользователями",
    description="Выполнение массового действия над выбранными пользователями",
    responses={
        200: {"description": "Результат выполнения операции"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        422: {"description": "Ошибка валидации"},
    }
)
async def bulk_user_action(
    action_data: UserManagementAction,
    current_user: User = Depends(get_current_admin),
    user_service: UserManagementService = Depends(get_user_management_service)
) -> BulkOperationResult:
    """
    Массовое действие над пользователями.
    
    Поддерживаемые действия:
    - activate: активация пользователей
    - deactivate: деактивация пользователей
    - promote: повышение роли
    - demote: понижение роли
    """
    try:
        result = await user_service.bulk_user_action(
            action_data=action_data,
            admin_id=current_user.id
        )
        
        logger.info(
            "Bulk user action completed",
            admin_id=current_user.id,
            action=action_data.action,
            affected_users=result.successful_items
        )
        
        return result
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error in bulk user action", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Аудит лог ===

@router.get(
    "/audit-log",
    response_model=AuditLogList,
    summary="Журнал аудита",
    description="Получение записей журнала аудита",
    responses={
        200: {"description": "Записи журнала аудита"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_audit_log(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Размер страницы"),
    actor_id: Optional[UUID] = Query(None, description="Фильтр по пользователю"),
    action: Optional[str] = Query(None, description="Фильтр по действию"),
    entity: Optional[str] = Query(None, description="Фильтр по сущности"),
    current_user: User = Depends(get_current_admin),
    audit_service: AuditLogService = Depends(get_audit_service)
) -> AuditLogList:
    """Получение записей журнала аудита."""
    try:
        filters = AuditLogFilters(
            actor_id=actor_id,
            action=action,
            entity=entity
        )
        
        audit_log = await audit_service.get_audit_log(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        return audit_log
    
    except Exception as e:
        logger.error("Error getting audit log", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Система и мониторинг ===

@router.get(
    "/system/health",
    response_model=SystemHealth,
    summary="Здоровье системы",
    description="Получение информации о состоянии системы",
    responses={
        200: {"description": "Состояние системы"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_system_health(
    current_user: User = Depends(get_current_admin),
    system_service: SystemManagementService = Depends(get_system_service)
) -> SystemHealth:
    """Получение состояния системы."""
    try:
        health = await system_service.get_system_health()
        
        logger.info("System health retrieved", admin_id=current_user.id)
        return health
    
    except Exception as e:
        logger.error("Error getting system health", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/system/metrics",
    response_model=SystemMetrics,
    summary="Системные метрики",
    description="Получение системных метрик производительности",
    responses={
        200: {"description": "Системные метрики"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_system_metrics(
    current_user: User = Depends(get_current_admin),
    system_service: SystemManagementService = Depends(get_system_service)
) -> SystemMetrics:
    """Получение системных метрик."""
    try:
        metrics = await system_service.get_system_metrics()
        
        logger.info("System metrics retrieved", admin_id=current_user.id)
        return metrics
    
    except Exception as e:
        logger.error("Error getting system metrics", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# === Экспорт данных ===

@router.post(
    "/export/users",
    summary="Экспорт пользователей",
    description="Создание задачи экспорта пользователей",
    responses={
        202: {"description": "Задача экспорта создана"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def export_users(
    format: str = Query("csv", description="Формат экспорта"),
    current_user: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Создание задачи экспорта пользователей."""
    # TODO: Реализовать экспорт через background tasks
    logger.info("User export requested", admin_id=current_user.id, format=format)
    
    return {
        "message": "Задача экспорта создана",
        "job_id": "export_job_123",
        "status": "pending"
    }


@router.post(
    "/export/bookings",
    summary="Экспорт бронирований",
    description="Создание задачи экспорта бронирований",
    responses={
        202: {"description": "Задача экспорта создана"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def export_bookings(
    format: str = Query("csv", description="Формат экспорта"),
    current_user: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Создание задачи экспорта бронирований."""
    # TODO: Реализовать экспорт через background tasks
    logger.info("Bookings export requested", admin_id=current_user.id, format=format)
    
    return {
        "message": "Задача экспорта создана",
        "job_id": "export_job_456",
        "status": "pending"
    }


# === Утилиты ===

@router.post(
    "/utils/send-test-email",
    summary="Отправить тестовое письмо",
    description="Отправка тестового письма для проверки email сервиса",
    responses={
        200: {"description": "Письмо отправлено"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        500: {"description": "Ошибка отправки"},
    }
)
async def send_test_email(
    recipient: str = Query(..., description="Email получателя"),
    current_user: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Отправка тестового письма."""
    # TODO: Реализовать отправку тестового письма
    logger.info("Test email requested", admin_id=current_user.id, recipient=recipient)
    
    return {
        "message": "Тестовое письмо отправлено",
        "recipient": recipient
    }


@router.post(
    "/utils/clear-cache",
    summary="Очистить кэш",
    description="Очистка кэша приложения",
    responses={
        200: {"description": "Кэш очищен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def clear_cache(
    current_user: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """Очистка кэша приложения."""
    # TODO: Реализовать очистку кэша
    logger.info("Cache clear requested", admin_id=current_user.id)
    
    return {
        "message": "Кэш очищен"
    }


@router.get(
    "/stats/quick",
    summary="Быстрая статистика",
    description="Получение быстрой статистики для виджетов",
    responses={
        200: {"description": "Быстрая статистика"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
    }
)
async def get_quick_stats(
    current_user: User = Depends(get_current_admin),
    dashboard_service: AdminDashboardService = Depends(get_dashboard_service)
) -> Dict[str, Any]:
    """Получение быстрой статистики для виджетов."""
    try:
        # Получаем только ключевые метрики
        stats = await dashboard_service.get_dashboard_stats()
        
        quick_stats = {
            "users_total": stats.total_users,
            "bookings_today": stats.new_bookings_today,
            "revenue_monthly": float(stats.monthly_revenue),
            "pending_moderation": stats.pending_bookings + stats.mentor_verifications_pending
        }
        
        return quick_stats
    
    except Exception as e:
        logger.error("Error getting quick stats", admin_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности админ модуля",
    description="Endpoint для проверки работоспособности административного модуля",
    responses={
        200: {"description": "Модуль работает корректно"},
    }
)
async def admin_health_check() -> Dict[str, Any]:
    """Проверка работоспособности административного модуля."""
    return {
        "status": "healthy",
        "module": "admin",
        "timestamp": "2024-09-10T19:30:00Z",
        "features": [
            "dashboard_stats",
            "platform_analytics",
            "moderation_queue",
            "user_management",
            "bulk_operations",
            "audit_log",
            "system_health",
            "system_metrics",
            "data_export",
            "admin_utilities"
        ]
    }


@router.post(
    "/payments/{booking_id}/verify",
    summary="Подтвердить оплату бронирования",
)
async def verify_payment(
    booking_id: UUID,
    _: Dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking.payment_status = "VERIFIED"
    booking.payment_verified_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    logger.info("Payment verified", booking_id=str(booking_id))
    return {
        "ok": True,
        "booking_id": str(booking_id),
        "payment_status": booking.payment_status,
        "payment_verified_at": booking.payment_verified_at.isoformat() if booking.payment_verified_at else None,
    }
