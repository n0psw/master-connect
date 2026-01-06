"""
Pydantic схемы для административного модуля.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator

from modules.bookings.domain.models import BookingStatus
from modules.users.domain.models import UserRole


class AdminDashboardStats(BaseModel):
    """Статистика для админской панели."""
    # Общие показатели
    total_users: int = Field(..., description="Общее количество пользователей")
    total_students: int = Field(..., description="Количество студентов")
    total_mentors: int = Field(..., description="Количество менторов")
    active_users: int = Field(..., description="Активных пользователей")
    
    # Бронирования
    total_bookings: int = Field(..., description="Всего бронирований")
    pending_bookings: int = Field(..., description="Ожидают модерации")
    completed_bookings: int = Field(..., description="Завершенных консультаций")
    
    # Финансы
    total_revenue: Decimal = Field(..., description="Общая выручка")
    pending_revenue: Decimal = Field(..., description="Ожидающая подтверждения выручка")
    monthly_revenue: Decimal = Field(..., description="Выручка за месяц")
    
    # За период
    new_users_today: int = Field(..., description="Новых пользователей сегодня")
    new_bookings_today: int = Field(..., description="Новых бронирований сегодня")
    mentor_verifications_pending: int = Field(..., description="Менторов на верификации")
    
    # Конверсия
    booking_conversion_rate: float = Field(..., description="Конверсия в бронирования (%)")
    payment_confirmation_rate: float = Field(..., description="Процент подтвержденных платежей")


class PlatformAnalytics(BaseModel):
    """Аналитика платформы."""
    period: str = Field(..., description="Период анализа")
    
    # Пользователи
    user_growth: List[Dict[str, Any]] = Field(..., description="Рост пользователей по дням")
    user_distribution: Dict[str, int] = Field(..., description="Распределение по ролям")
    top_countries: List[Dict[str, Any]] = Field(..., description="Топ стран пользователей")
    
    # Бронирования
    booking_trends: List[Dict[str, Any]] = Field(..., description="Тренды бронирований")
    booking_status_distribution: Dict[str, int] = Field(..., description="Распределение по статусам")
    popular_duration: List[Dict[str, Any]] = Field(..., description="Популярные длительности")
    
    # Менторы
    top_mentors: List[Dict[str, Any]] = Field(..., description="Топ менторы по бронированиям")
    mentor_subjects: List[Dict[str, Any]] = Field(..., description="Популярные предметы")
    mentor_rating_distribution: List[Dict[str, Any]] = Field(..., description="Распределение рейтингов")
    
    # Финансы
    revenue_trends: List[Dict[str, Any]] = Field(..., description="Тренды выручки")
    average_session_price: Decimal = Field(..., description="Средняя стоимость сессии")


class ModerationQueue(BaseModel):
    """Очередь модерации."""
    # Менторы на верификацию
    pending_mentor_verifications: List[Dict[str, Any]] = Field(..., description="Менторы на верификацию")
    
    # Платежи на подтверждение  
    pending_payments: List[Dict[str, Any]] = Field(..., description="Платежи на подтверждение")
    
    # Жалобы и обращения
    open_support_tickets: List[Dict[str, Any]] = Field(..., description="Открытые тикеты поддержки")
    
    # Проблемы требующие внимания
    issues_requiring_attention: List[Dict[str, Any]] = Field(..., description="Проблемы требующие внимания")


class UserManagementFilters(BaseModel):
    """Фильтры для управления пользователями."""
    role: Optional[UserRole] = Field(None, description="Фильтр по роли")
    is_active: Optional[bool] = Field(None, description="Фильтр по активности")
    created_from: Optional[date] = Field(None, description="Создан после даты")
    created_to: Optional[date] = Field(None, description="Создан до даты")
    country: Optional[str] = Field(None, description="Фильтр по стране")
    search: Optional[str] = Field(None, description="Поиск по имени или email")


class CreateMentorRequest(BaseModel):
    """Запрос на создание ментора администратором."""
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=8, description="Пароль")
    name: str = Field(..., min_length=2, max_length=255, description="Имя")
    phone: Optional[str] = Field(None, description="Телефон")
    bio: Optional[str] = Field(None, description="Биография")
    headline: Optional[str] = Field(None, max_length=255, description="Заголовок профиля")
    price_30: Optional[Decimal] = Field(None, ge=0, description="Цена за 30 минут")
    price_45: Optional[Decimal] = Field(None, ge=0, description="Цена за 45 минут")
    price_60: Optional[Decimal] = Field(None, ge=0, description="Цена за 60 минут")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    languages: Optional[List[str]] = Field(default_factory=list, description="Языки")
    send_welcome_email: bool = Field(True, description="Отправить приветственное письмо")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError("Пароль должен содержать буквы и цифры")
        return v


class CreateMentorResponse(BaseModel):
    """Ответ на создание ментора."""
    user_id: UUID = Field(..., description="ID созданного пользователя")
    mentor_id: UUID = Field(..., description="ID профиля ментора")
    email: str = Field(..., description="Email")
    name: str = Field(..., description="Имя")
    message: str = Field(..., description="Сообщение о результате")


class UserManagementAction(BaseModel):
    """Действие над пользователем."""
    action: str = Field(..., description="Действие (activate, deactivate, promote, demote)")
    user_ids: List[UUID] = Field(..., min_items=1, description="ID пользователей")
    reason: Optional[str] = Field(None, description="Причина действия")
    new_role: Optional[UserRole] = Field(None, description="Новая роль (для promote/demote)")
    send_notification: bool = Field(True, description="Отправить уведомление пользователю")


class MentorModerationAction(BaseModel):
    """Действие модерации ментора."""
    action: str = Field(..., description="Действие (verify, reject, suspend)")
    mentor_ids: List[UUID] = Field(..., min_items=1, description="ID менторов")
    verification_note: Optional[str] = Field(None, description="Заметка о верификации")
    rejection_reason: Optional[str] = Field(None, description="Причина отклонения")
    send_notification: bool = Field(True, description="Отправить уведомление")


class BookingModerationAction(BaseModel):
    """Действие модерации бронирования."""
    action: str = Field(..., description="Действие (confirm_payment, reject_payment, cancel, reschedule)")
    booking_ids: List[UUID] = Field(..., min_items=1, description="ID бронирований")
    payment_reference: Optional[str] = Field(None, description="Номер транзакции")
    admin_notes: Optional[str] = Field(None, description="Заметки администратора")
    new_starts_at: Optional[datetime] = Field(None, description="Новое время (для переноса)")
    send_notification: bool = Field(True, description="Отправить уведомления")


class SystemSettings(BaseModel):
    """Системные настройки платформы."""
    # Общие настройки
    platform_name: str = Field(..., description="Название платформы")
    platform_description: str = Field(..., description="Описание платформы")
    support_email: str = Field(..., description="Email поддержки")
    maintenance_mode: bool = Field(False, description="Режим обслуживания")
    
    # Настройки бронирования
    booking_hold_duration_minutes: int = Field(10, description="Время удержания бронирования (минуты)")
    max_future_booking_days: int = Field(90, description="Максимум дней для бронирования вперед")
    cancellation_deadline_hours: int = Field(2, description="Крайний срок отмены (часы)")
    
    # Настройки платежей
    kaspi_payment_url: str = Field(..., description="Ссылка на Kaspi Pay")
    auto_payment_verification: bool = Field(False, description="Автоматическая верификация платежей")
    
    # Настройки уведомлений
    email_notifications_enabled: bool = Field(True, description="Email уведомления включены")
    reminder_24h_enabled: bool = Field(True, description="Напоминание за 24 часа")
    reminder_1h_enabled: bool = Field(True, description="Напоминание за 1 час")
    
    # Настройки менторов
    mentor_auto_verification: bool = Field(False, description="Автоматическая верификация менторов")
    mentor_max_universities: int = Field(5, description="Максимум университетов у ментора")
    
    # Настройки файлов
    max_file_size_mb: int = Field(10, description="Максимальный размер файла (MB)")
    allowed_file_types: List[str] = Field(["pdf", "jpg", "jpeg", "png", "docx"], description="Разрешенные типы файлов")


class AuditLogEntry(BaseModel):
    """Запись аудит лога."""
    id: UUID = Field(..., description="ID записи")
    actor_id: UUID = Field(..., description="ID пользователя, выполнившего действие")
    actor_email: str = Field(..., description="Email пользователя")
    action: str = Field(..., description="Выполненное действие")
    entity: str = Field(..., description="Сущность")
    entity_id: UUID = Field(..., description="ID сущности")
    meta: Dict[str, Any] = Field(..., description="Дополнительные данные")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent")
    created_at: datetime = Field(..., description="Время действия")


class AuditLogFilters(BaseModel):
    """Фильтры для аудит лога."""
    actor_id: Optional[UUID] = Field(None, description="Фильтр по пользователю")
    action: Optional[str] = Field(None, description="Фильтр по действию")
    entity: Optional[str] = Field(None, description="Фильтр по сущности")
    date_from: Optional[datetime] = Field(None, description="Начальная дата")
    date_to: Optional[datetime] = Field(None, description="Конечная дата")


class AuditLogList(BaseModel):
    """Список записей аудит лога."""
    entries: List[AuditLogEntry] = Field(..., description="Записи лога")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    page_size: int = Field(..., description="Размер страницы")


class AdminNotification(BaseModel):
    """Уведомление для администраторов."""
    id: UUID = Field(..., description="ID уведомления")
    type: str = Field(..., description="Тип уведомления")
    title: str = Field(..., description="Заголовок")
    message: str = Field(..., description="Сообщение")
    severity: str = Field(..., description="Важность (info, warning, error)")
    entity_type: Optional[str] = Field(None, description="Тип связанной сущности")
    entity_id: Optional[UUID] = Field(None, description="ID связанной сущности")
    is_read: bool = Field(False, description="Прочитано")
    created_at: datetime = Field(..., description="Время создания")


class SystemHealth(BaseModel):
    """Состояние системы."""
    status: str = Field(..., description="Общий статус (healthy, degraded, down)")
    database_status: str = Field(..., description="Статус базы данных")
    email_service_status: str = Field(..., description="Статус email сервиса")
    storage_status: str = Field(..., description="Статус файлового хранилища")
    
    # Метрики
    active_connections: int = Field(..., description="Активных соединений")
    memory_usage_percent: float = Field(..., description="Использование памяти (%)")
    disk_usage_percent: float = Field(..., description="Использование диска (%)")
    
    # Версии
    api_version: str = Field(..., description="Версия API")
    database_version: str = Field(..., description="Версия базы данных")
    
    last_check: datetime = Field(..., description="Время последней проверки")


class BulkOperationResult(BaseModel):
    """Результат массовой операции."""
    total_items: int = Field(..., description="Общее количество элементов")
    successful_items: int = Field(..., description="Успешно обработано")
    failed_items: int = Field(..., description="Не удалось обработать")
    errors: List[str] = Field(default=[], description="Ошибки")
    
    # Детали
    affected_ids: List[UUID] = Field(default=[], description="ID затронутых элементов")
    operation_id: UUID = Field(..., description="ID операции")
    started_at: datetime = Field(..., description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")


class ExportRequest(BaseModel):
    """Запрос на экспорт данных."""
    export_type: str = Field(..., description="Тип экспорта (users, bookings, revenue)")
    format: str = Field("csv", description="Формат файла (csv, xlsx, json)")
    filters: Dict[str, Any] = Field(default={}, description="Фильтры для экспорта")
    date_from: Optional[date] = Field(None, description="Начальная дата")
    date_to: Optional[date] = Field(None, description="Конечная дата")
    include_personal_data: bool = Field(False, description="Включать персональные данные")


class ExportJob(BaseModel):
    """Задача экспорта."""
    id: UUID = Field(..., description="ID задачи")
    export_type: str = Field(..., description="Тип экспорта")
    status: str = Field(..., description="Статус (pending, processing, completed, failed)")
    progress_percent: int = Field(0, description="Прогресс выполнения (%)")
    file_url: Optional[str] = Field(None, description="Ссылка на файл")
    file_size: Optional[int] = Field(None, description="Размер файла в байтах")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    created_by: UUID = Field(..., description="ID создавшего пользователя")
    created_at: datetime = Field(..., description="Время создания")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    expires_at: datetime = Field(..., description="Время истечения ссылки")


class AdminActionLog(BaseModel):
    """Лог действий администратора."""
    id: UUID = Field(..., description="ID записи")
    admin_id: UUID = Field(..., description="ID администратора")
    admin_email: str = Field(..., description="Email администратора")
    action_type: str = Field(..., description="Тип действия")
    target_type: str = Field(..., description="Тип цели действия")
    target_id: UUID = Field(..., description="ID цели")
    description: str = Field(..., description="Описание действия")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Старые значения")
    new_values: Optional[Dict[str, Any]] = Field(None, description="Новые значения")
    created_at: datetime = Field(..., description="Время действия")
    severity: str = Field("info", description="Важность (info, warning, critical)")


class SystemMetrics(BaseModel):
    """Системные метрики."""
    timestamp: datetime = Field(..., description="Время сбора метрик")
    
    # API метрики
    requests_per_minute: int = Field(..., description="Запросов в минуту")
    average_response_time: float = Field(..., description="Среднее время ответа (мс)")
    error_rate_percent: float = Field(..., description="Процент ошибок")
    
    # База данных
    db_connections_active: int = Field(..., description="Активных подключений к БД")
    db_query_avg_time: float = Field(..., description="Среднее время запроса к БД (мс)")
    
    # Пользователи
    online_users: int = Field(..., description="Пользователей онлайн")
    active_sessions: int = Field(..., description="Активных сессий")
    
    # Бизнес метрики
    bookings_per_hour: int = Field(..., description="Бронирований в час")
    revenue_per_hour: Decimal = Field(..., description="Выручка в час")


class FeatureFlag(BaseModel):
    """Флаг функциональности."""
    name: str = Field(..., description="Название флага")
    key: str = Field(..., description="Ключ флага")
    is_enabled: bool = Field(..., description="Включен ли флаг")
    description: str = Field(..., description="Описание функциональности")
    target_audience: str = Field("all", description="Целевая аудитория (all, students, mentors, admins)")
    rollout_percent: int = Field(100, description="Процент раскрытия (0-100)")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")


class FeatureFlagUpdate(BaseModel):
    """Обновление флага функциональности."""
    is_enabled: Optional[bool] = Field(None, description="Включен ли флаг")
    target_audience: Optional[str] = Field(None, description="Целевая аудитория")
    rollout_percent: Optional[int] = Field(None, ge=0, le=100, description="Процент раскрытия")
    description: Optional[str] = Field(None, description="Описание")
