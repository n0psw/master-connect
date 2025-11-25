"""
Модуль уведомлений.
"""
from modules.notifications.domain.models import Notification, NotificationType
from modules.notifications.api.routes import router

__all__ = ["Notification", "NotificationType", "router"]

