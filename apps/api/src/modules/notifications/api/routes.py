"""
API роуты для модуля уведомлений.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_active_user
from core.exceptions import NotFoundError
from core.logging import get_logger
from db.session import get_db
from modules.notifications.application.services import NotificationService
from modules.notifications.domain.schemas import (
    NotificationList,
    NotificationResponse,
    UnreadCount,
)
from modules.users.domain.models import User

logger = get_logger(__name__)

router = APIRouter(prefix="/notifications", tags=["Уведомления"])


async def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    """Dependency для получения сервиса уведомлений."""
    return NotificationService(db)


@router.get(
    "",
    response_model=NotificationList,
    summary="Получить список уведомлений",
    description="Получение списка уведомлений текущего пользователя",
    responses={
        200: {"description": "Список уведомлений"},
        401: {"description": "Требуется авторизация"},
    }
)
async def get_notifications(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    is_read: bool = Query(None, description="Фильтр по прочитанности"),
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
) -> NotificationList:
    """
    Получение списка уведомлений текущего пользователя.
    
    Поддерживает пагинацию и фильтрацию по прочитанности.
    """
    try:
        notifications, total, unread_count = await service.get_user_notifications(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            is_read=is_read
        )
        
        return NotificationList(
            notifications=notifications,
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error("Error getting notifications", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/unread/count",
    response_model=UnreadCount,
    summary="Получить количество непрочитанных уведомлений",
    description="Получение количества непрочитанных уведомлений пользователя",
    responses={
        200: {"description": "Количество непрочитанных уведомлений"},
        401: {"description": "Требуется авторизация"},
    }
)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
) -> UnreadCount:
    """
    Получение количества непрочитанных уведомлений.
    """
    try:
        count = await service.get_unread_count(current_user.id)
        return UnreadCount(count=count)
    
    except Exception as e:
        logger.error("Error getting unread count", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Отметить уведомление как прочитанное",
    description="Отметка уведомления как прочитанного",
    responses={
        200: {"description": "Уведомление отмечено как прочитанное"},
        401: {"description": "Требуется авторизация"},
        404: {"description": "Уведомление не найдено"},
    }
)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
) -> NotificationResponse:
    """
    Отметка уведомления как прочитанного.
    """
    try:
        notification = await service.mark_as_read(notification_id, current_user.id)
        return notification
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    except Exception as e:
        logger.error("Error marking notification as read", notification_id=notification_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/mark-all-read",
    status_code=status.HTTP_200_OK,
    summary="Отметить все уведомления как прочитанные",
    description="Отметка всех уведомлений пользователя как прочитанных",
    responses={
        200: {"description": "Все уведомления отмечены как прочитанные"},
        401: {"description": "Требуется авторизация"},
    }
)
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
) -> dict:
    """
    Отметка всех уведомлений как прочитанных.
    """
    try:
        count = await service.mark_all_as_read(current_user.id)
        return {"marked_count": count}
    
    except Exception as e:
        logger.error("Error marking all as read", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить уведомление",
    description="Удаление уведомления",
    responses={
        204: {"description": "Уведомление удалено"},
        401: {"description": "Требуется авторизация"},
        404: {"description": "Уведомление не найдено"},
    }
)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
) -> None:
    """
    Удаление уведомления.
    """
    try:
        await service.delete_notification(notification_id, current_user.id)
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    except Exception as e:
        logger.error("Error deleting notification", notification_id=notification_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

