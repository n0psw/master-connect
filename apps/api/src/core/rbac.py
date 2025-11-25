"""
Role-Based Access Control (RBAC) система.
"""
from enum import Enum
from typing import List, Set

from modules.users.domain.models import UserRole


class Permission(str, Enum):
    """Разрешения в системе."""
    
    # Общие разрешения
    READ_OWN_PROFILE = "read_own_profile"
    UPDATE_OWN_PROFILE = "update_own_profile"
    DELETE_OWN_PROFILE = "delete_own_profile"
    
    # Менторы
    READ_MENTORS = "read_mentors"
    READ_MENTOR_DETAILS = "read_mentor_details"
    READ_MENTOR_SLOTS = "read_mentor_slots"
    
    # Управление профилем ментора
    UPDATE_MENTOR_PROFILE = "update_mentor_profile"
    MANAGE_MENTOR_AVAILABILITY = "manage_mentor_availability"
    MANAGE_MENTOR_TIME_OFF = "manage_mentor_time_off"
    
    # Бронирования - студент
    CREATE_BOOKING = "create_booking"
    CANCEL_OWN_BOOKING = "cancel_own_booking"
    READ_OWN_BOOKINGS = "read_own_bookings"
    MARK_PAYMENT = "mark_payment"  # "Я оплатил"
    
    # Бронирования - ментор
    READ_MENTOR_BOOKINGS = "read_mentor_bookings"
    UPDATE_BOOKING_DETAILS = "update_booking_details"  # для переносов
    
    # Отзывы
    CREATE_REVIEW = "create_review"
    READ_REVIEWS = "read_reviews"
    READ_OWN_REVIEWS = "read_own_reviews"
    
    # Чат
    SEND_MESSAGE = "send_message"
    READ_MESSAGES = "read_messages"
    UPLOAD_FILE = "upload_file"
    
    # Поддержка
    CREATE_SUPPORT_TICKET = "create_support_ticket"
    READ_OWN_SUPPORT_TICKETS = "read_own_support_tickets"
    
    # Администраторские разрешения
    # Модерация менторов
    READ_ALL_MENTORS = "read_all_mentors"
    MODERATE_MENTORS = "moderate_mentors"
    VERIFY_MENTORS = "verify_mentors"
    
    # Управление платежами
    READ_PAYMENT_QUEUE = "read_payment_queue"
    CONFIRM_PAYMENT = "confirm_payment"
    REJECT_PAYMENT = "reject_payment"
    
    # Управление бронированиями
    READ_ALL_BOOKINGS = "read_all_bookings"
    UPDATE_ANY_BOOKING = "update_any_booking"
    RESCHEDULE_BOOKING = "reschedule_booking"
    CANCEL_ANY_BOOKING = "cancel_any_booking"
    
    # Управление пользователями
    READ_ALL_USERS = "read_all_users"
    UPDATE_USER = "update_user"
    DEACTIVATE_USER = "deactivate_user"
    
    # Поддержка (админ)
    READ_ALL_SUPPORT_TICKETS = "read_all_support_tickets"
    UPDATE_SUPPORT_TICKET = "update_support_ticket"
    CLOSE_SUPPORT_TICKET = "close_support_ticket"
    
    # Управление чатом
    MODERATE_CHAT = "moderate_chat"
    BLOCK_DIALOG = "block_dialog"
    
    # Системные настройки
    READ_SYSTEM_SETTINGS = "read_system_settings"
    UPDATE_SYSTEM_SETTINGS = "update_system_settings"
    
    # Аналитика и отчеты
    READ_ANALYTICS = "read_analytics"
    EXPORT_DATA = "export_data"
    
    # Аудит
    READ_AUDIT_LOG = "read_audit_log"


# Матрица ролей и разрешений
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.STUDENT: {
        # Профиль
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.DELETE_OWN_PROFILE,
        
        # Менторы
        Permission.READ_MENTORS,
        Permission.READ_MENTOR_DETAILS,
        Permission.READ_MENTOR_SLOTS,
        
        # Бронирования
        Permission.CREATE_BOOKING,
        Permission.CANCEL_OWN_BOOKING,
        Permission.READ_OWN_BOOKINGS,
        Permission.MARK_PAYMENT,
        
        # Отзывы
        Permission.CREATE_REVIEW,
        Permission.READ_REVIEWS,
        Permission.READ_OWN_REVIEWS,
        
        # Чат
        Permission.SEND_MESSAGE,
        Permission.READ_MESSAGES,
        Permission.UPLOAD_FILE,
        
        # Поддержка
        Permission.CREATE_SUPPORT_TICKET,
        Permission.READ_OWN_SUPPORT_TICKETS,
    },
    
    UserRole.MENTOR: {
        # Профиль
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        Permission.DELETE_OWN_PROFILE,
        
        # Управление профилем ментора
        Permission.UPDATE_MENTOR_PROFILE,
        Permission.MANAGE_MENTOR_AVAILABILITY,
        Permission.MANAGE_MENTOR_TIME_OFF,
        
        # Менторы (для просмотра других)
        Permission.READ_MENTORS,
        Permission.READ_MENTOR_DETAILS,
        
        # Бронирования
        Permission.READ_MENTOR_BOOKINGS,
        Permission.UPDATE_BOOKING_DETAILS,
        
        # Отзывы
        Permission.READ_REVIEWS,
        Permission.READ_OWN_REVIEWS,
        
        # Чат
        Permission.SEND_MESSAGE,
        Permission.READ_MESSAGES,
        Permission.UPLOAD_FILE,
        
        # Поддержка
        Permission.CREATE_SUPPORT_TICKET,
        Permission.READ_OWN_SUPPORT_TICKETS,
    },
    
    UserRole.ADMIN: {
        # Все разрешения администратора
        permission for permission in Permission
    },
}


def get_user_permissions(user_role: UserRole) -> Set[Permission]:
    """Получение разрешений для роли пользователя."""
    return ROLE_PERMISSIONS.get(user_role, set())


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Проверка наличия разрешения у роли."""
    user_permissions = get_user_permissions(user_role)
    return permission in user_permissions


def has_any_permission(user_role: UserRole, permissions: List[Permission]) -> bool:
    """Проверка наличия любого из разрешений у роли."""
    user_permissions = get_user_permissions(user_role)
    return any(permission in user_permissions for permission in permissions)


def has_all_permissions(user_role: UserRole, permissions: List[Permission]) -> bool:
    """Проверка наличия всех разрешений у роли."""
    user_permissions = get_user_permissions(user_role)
    return all(permission in user_permissions for permission in permissions)


def can_access_resource(user_role: UserRole, resource_type: str, action: str) -> bool:
    """
    Проверка доступа к ресурсу на основе типа ресурса и действия.
    
    Args:
        user_role: Роль пользователя
        resource_type: Тип ресурса (booking, mentor, user и т.д.)
        action: Действие (read, create, update, delete)
    
    Returns:
        bool: Есть ли доступ
    """
    # Мапинг ресурсов и действий на разрешения
    resource_permission_map = {
        ("mentor", "read"): Permission.READ_MENTORS,
        ("mentor", "update"): Permission.UPDATE_MENTOR_PROFILE,
        ("mentor", "moderate"): Permission.MODERATE_MENTORS,
        
        ("booking", "create"): Permission.CREATE_BOOKING,
        ("booking", "read_own"): Permission.READ_OWN_BOOKINGS,
        ("booking", "read_all"): Permission.READ_ALL_BOOKINGS,
        ("booking", "update"): Permission.UPDATE_ANY_BOOKING,
        ("booking", "confirm_payment"): Permission.CONFIRM_PAYMENT,
        
        ("user", "read_all"): Permission.READ_ALL_USERS,
        ("user", "update"): Permission.UPDATE_USER,
        
        ("support", "read_own"): Permission.READ_OWN_SUPPORT_TICKETS,
        ("support", "read_all"): Permission.READ_ALL_SUPPORT_TICKETS,
        ("support", "update"): Permission.UPDATE_SUPPORT_TICKET,
        
        ("settings", "read"): Permission.READ_SYSTEM_SETTINGS,
        ("settings", "update"): Permission.UPDATE_SYSTEM_SETTINGS,
        
        ("audit", "read"): Permission.READ_AUDIT_LOG,
    }
    
    permission = resource_permission_map.get((resource_type, action))
    if permission:
        return has_permission(user_role, permission)
    
    return False


class RoleChecker:
    """Класс для проверки ролей и разрешений."""
    
    def __init__(self, allowed_roles: List[UserRole] = None, required_permissions: List[Permission] = None):
        self.allowed_roles = allowed_roles or []
        self.required_permissions = required_permissions or []
    
    def __call__(self, user_role: UserRole) -> bool:
        """Проверка доступа."""
        # Проверка роли
        if self.allowed_roles and user_role not in self.allowed_roles:
            return False
        
        # Проверка разрешений
        if self.required_permissions:
            return has_all_permissions(user_role, self.required_permissions)
        
        return True


# Предопределенные проверки ролей
admin_required = RoleChecker(allowed_roles=[UserRole.ADMIN])
mentor_or_admin = RoleChecker(allowed_roles=[UserRole.MENTOR, UserRole.ADMIN])
student_or_admin = RoleChecker(allowed_roles=[UserRole.STUDENT, UserRole.ADMIN])
any_authenticated = RoleChecker(allowed_roles=[UserRole.STUDENT, UserRole.MENTOR, UserRole.ADMIN])

