"""
Сервисы для модуля уведомлений.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError
from core.logging import get_logger
from modules.notifications.domain.models import Notification, NotificationType
from modules.notifications.domain.schemas import (
    NotificationCreate,
    NotificationList,
    NotificationResponse,
    UnreadCount,
)
from modules.notifications.application.ws_manager import ws_manager

logger = get_logger(__name__)


class NotificationService:
    """Сервис для управления уведомлениями."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """Создание нового уведомления."""
        logger.info(
            "Creating notification",
            user_id=notification_data.user_id,
            type=notification_data.type
        )
        
        notification = Notification(
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            related_entity_type=notification_data.related_entity_type,
            related_entity_id=notification_data.related_entity_id,
            action_url=notification_data.action_url,
            is_read=False
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        logger.info("Notification created", notification_id=notification.id)
        
        response = NotificationResponse.from_orm(notification)

        try:
            unread = await self.get_unread_count(notification.user_id)
            await ws_manager.send_to_user(
                user_id=notification.user_id,
                message={
                    "type": "notification",
                    "payload": response.model_dump(mode="json"),
                    "unread_count": unread,
                },
            )
        except Exception as e:
            logger.warning("Failed to push notification via WS", notification_id=notification.id, error=str(e))

        return response
    
    async def get_user_notifications(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        is_read: Optional[bool] = None
    ) -> Tuple[List[NotificationResponse], int, int]:
        """Получение уведомлений пользователя."""
        offset = (page - 1) * page_size
        
        # Базовый запрос
        query = select(Notification).where(Notification.user_id == user_id)
        
        # Фильтр по прочитанности
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        
        # Сортировка (сначала непрочитанные, потом по дате)
        query = query.order_by(Notification.is_read.asc(), desc(Notification.created_at))
        
        # Подсчет общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Подсчет непрочитанных
        unread_query = select(func.count()).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        unread_result = await self.db.execute(unread_query)
        unread_count = unread_result.scalar() or 0
        
        # Пагинация
        query = query.limit(page_size).offset(offset)
        
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        responses = [NotificationResponse.from_orm(n) for n in notifications]
        
        return responses, total, unread_count
    
    async def get_unread_count(self, user_id: UUID) -> int:
        """Получение количества непрочитанных уведомлений."""
        query = select(func.count()).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return count
    
    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> NotificationResponse:
        """Отметка уведомления как прочитанного."""
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise NotFoundError("Notification", str(notification_id))
        
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(notification)
            
            logger.info("Notification marked as read", notification_id=notification_id)
        
        return NotificationResponse.from_orm(notification)
    
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Отметка всех уведомлений пользователя как прочитанных."""
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        result = await self.db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        now = datetime.utcnow()
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
            count += 1
        
        if count > 0:
            await self.db.commit()
            logger.info("Marked all notifications as read", user_id=user_id, count=count)
        
        return count
    
    async def delete_notification(self, notification_id: UUID, user_id: UUID) -> None:
        """Удаление уведомления."""
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise NotFoundError("Notification", str(notification_id))
        
        await self.db.delete(notification)
        await self.db.commit()
        
        logger.info("Notification deleted", notification_id=notification_id)


# Вспомогательная функция для создания уведомлений в других модулях
async def create_notification_helper(
    db: AsyncSession,
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[UUID] = None,
    action_url: Optional[str] = None
) -> None:
    """Вспомогательная функция для создания уведомлений из других модулей."""
    service = NotificationService(db)
    
    notification_data = NotificationCreate(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        action_url=action_url
    )
    
    await service.create_notification(notification_data)

