"""
Pydantic схемы для модуля бронирований.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from modules.bookings.domain.models import BookingStatus


class BookingIntakeForm(BaseModel):
    """Форма подачи заявки на консультацию."""
    # Обязательные поля
    goals: str = Field(..., min_length=10, max_length=1000, description="Цели консультации")
    current_situation: str = Field(..., min_length=10, max_length=1000, description="Текущая ситуация")
    specific_questions: List[str] = Field(..., min_items=1, max_items=5, description="Конкретные вопросы")
    
    # Дополнительная информация
    preparation_level: Optional[str] = Field(None, max_length=500, description="Уровень подготовки")
    previous_experience: Optional[str] = Field(None, max_length=500, description="Предыдущий опыт")
    expected_outcome: Optional[str] = Field(None, max_length=500, description="Ожидаемый результат")
    additional_info: Optional[str] = Field(None, max_length=1000, description="Дополнительная информация")
    
    @field_validator("specific_questions")
    @classmethod
    def validate_questions(cls, v):
        """Валидация вопросов."""
        if not isinstance(v, list):
            raise ValueError("Вопросы должны быть списком")
        
        # Проверяем каждый вопрос
        for question in v:
            if not question or len(question.strip()) < 5:
                raise ValueError("Каждый вопрос должен содержать минимум 5 символов")
        
        return v


class BookingCreate(BaseModel):
    """Схема для создания бронирования."""
    mentor_id: UUID = Field(..., description="ID ментора")
    starts_at: datetime = Field(..., description="Время начала консультации")
    duration_minutes: int = Field(..., ge=30, le=120, description="Длительность в минутах")
    intake_form: BookingIntakeForm = Field(..., description="Форма подачи заявки")
    notes: Optional[str] = Field(None, max_length=500, description="Дополнительные заметки")
    
    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, v):
        """Валидация длительности."""
        if v not in [30, 45, 60]:
            raise ValueError("Длительность должна быть 30, 45 или 60 минут")
        return v
    
    @field_validator("starts_at")
    @classmethod
    def validate_future_date(cls, v):
        """Проверка, что дата в будущем."""
        now = datetime.now(timezone.utc)
        # Приводим к одному типу (aware)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("Время начала должно быть в будущем")
        return v


class BookingUpdate(BaseModel):
    """Схема для обновления бронирования."""
    starts_at: Optional[datetime] = Field(None, description="Новое время начала")
    notes: Optional[str] = Field(None, max_length=500, description="Заметки")
    intake_form: Optional[BookingIntakeForm] = Field(None, description="Обновленная форма заявки")
    
    @field_validator("starts_at")
    @classmethod
    def validate_future_date(cls, v):
        """Проверка, что дата в будущем."""
        if v:
            now = datetime.now(timezone.utc)
            # Приводим к одному типу (aware)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= now:
                raise ValueError("Время начала должно быть в будущем")
        return v


class BookingResponse(BaseModel):
    """Схема ответа с информацией о бронировании."""
    id: UUID = Field(..., description="ID бронирования")
    student_id: UUID = Field(..., description="ID студента")
    mentor_id: UUID = Field(..., description="ID ментора")
    starts_at: datetime = Field(..., description="Время начала")
    ends_at: datetime = Field(..., description="Время окончания")
    duration_minutes: int = Field(..., description="Длительность в минутах")
    status: BookingStatus = Field(..., description="Статус бронирования")
    price_amount: Decimal = Field(..., description="Стоимость")
    price_currency: str = Field(..., description="Валюта")
    
    # Связанные данные
    hold_expires_at: Optional[datetime] = Field(None, description="Истечение холда")
    google_meet_link: Optional[str] = Field(None, description="Ссылка на Google Meet")
    google_calendar_event_id: Optional[str] = Field(None, description="ID события в календаре")
    
    # Метаданные
    intake_form: Dict[str, Any] = Field(..., description="Форма подачи заявки")
    notes: Optional[str] = Field(None, description="Заметки")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    # Информация о менторе (краткая)
    mentor_name: str = Field(..., description="Имя ментора")
    mentor_email: Optional[str] = Field(None, description="Email ментора")
    mentor_avatar_url: Optional[str] = Field(None, description="Аватар ментора")
    
    # Информация о студенте (краткая)
    student_name: str = Field(..., description="Имя студента")
    student_email: Optional[str] = Field(None, description="Email студента")
    student_avatar_url: Optional[str] = Field(None, description="Аватар студента")
    
    # Информация об отзыве
    has_review: bool = Field(False, description="Есть ли уже отзыв на это бронирование")
    
    class Config:
        from_attributes = True


class BookingDetail(BaseModel):
    """Детальная информация о бронировании."""
    booking: BookingResponse = Field(..., description="Основная информация о бронировании")
    can_cancel: bool = Field(..., description="Можно ли отменить")
    can_reschedule: bool = Field(..., description="Можно ли перенести")
    can_mark_payment: bool = Field(..., description="Можно ли отметить оплату")
    cancellation_deadline: Optional[datetime] = Field(None, description="Крайний срок отмены")
    reschedule_deadline: Optional[datetime] = Field(None, description="Крайний срок переноса")


class BookingList(BaseModel):
    """Список бронирований."""
    bookings: List[BookingResponse] = Field(..., description="Список бронирований")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    page_size: int = Field(..., description="Размер страницы")
    total_pages: int = Field(..., description="Общее количество страниц")


class BookingStatusUpdate(BaseModel):
    """Обновление статуса бронирования."""
    status: BookingStatus = Field(..., description="Новый статус")
    reason: Optional[str] = Field(None, max_length=500, description="Причина изменения статуса")
    admin_notes: Optional[str] = Field(None, max_length=1000, description="Заметки администратора")


class BookingPaymentConfirmation(BaseModel):
    """Подтверждение оплаты бронирования."""
    payment_confirmed: bool = Field(..., description="Оплата подтверждена")
    payment_notes: Optional[str] = Field(None, max_length=500, description="Заметки об оплате")
    payment_reference: Optional[str] = Field(None, max_length=255, description="Номер транзакции")


class BookingStats(BaseModel):
    """Статистика бронирований."""
    total_bookings: int = Field(..., description="Общее количество бронирований")
    pending_payment: int = Field(..., description="Ожидают подтверждения оплаты")
    confirmed: int = Field(..., description="Подтвержденные")
    completed: int = Field(..., description="Завершенные")
    cancelled: int = Field(..., description="Отмененные")
    
    # По времени
    today: int = Field(..., description="Бронирований сегодня")
    this_week: int = Field(..., description="Бронирований на этой неделе")
    this_month: int = Field(..., description="Бронирований в этом месяце")
    
    # Финансовые
    total_revenue: Decimal = Field(..., description="Общая выручка")
    pending_revenue: Decimal = Field(..., description="Ожидающая выручка")
    
    # Средние показатели
    average_session_duration: float = Field(..., description="Средняя длительность сессии")
    average_price: Decimal = Field(..., description="Средняя цена")


class BookingFilters(BaseModel):
    """Фильтры для поиска бронирований."""
    status: Optional[List[BookingStatus]] = Field(None, description="Фильтр по статусам")
    mentor_id: Optional[UUID] = Field(None, description="Фильтр по ментору")
    student_id: Optional[UUID] = Field(None, description="Фильтр по студенту")
    date_from: Optional[datetime] = Field(None, description="Дата начала периода")
    date_to: Optional[datetime] = Field(None, description="Дата окончания периода")
    search: Optional[str] = Field(None, description="Поиск по имени студента/ментора или email")
    duration_minutes: Optional[int] = Field(None, description="Фильтр по длительности")
    upcoming: Optional[bool] = Field(None, description="Только предстоящие (starts_at > now)")
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Валидация диапазона дат."""
        if self.date_to and self.date_from and self.date_to < self.date_from:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return self


class BookingRescheduleRequest(BaseModel):
    """Запрос на перенос бронирования."""
    new_starts_at: datetime = Field(..., description="Новое время начала")
    reason: Optional[str] = Field(None, max_length=500, description="Причина переноса")
    
    @field_validator("new_starts_at")
    @classmethod
    def validate_future_date(cls, v):
        """Проверка, что новая дата в будущем."""
        now = datetime.now(timezone.utc)
        # Приводим к одному типу (aware)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("Новое время начала должно быть в будущем")
        return v


class BookingCancellationRequest(BaseModel):
    """Запрос на отмену бронирования."""
    reason: str = Field(..., min_length=5, max_length=500, description="Причина отмены")
    request_refund: bool = Field(False, description="Запросить возврат средств")


class PaymentInfo(BaseModel):
    """Информация о платеже."""
    booking_id: UUID = Field(..., description="ID бронирования")
    amount: Decimal = Field(..., description="Сумма платежа")
    currency: str = Field(..., description="Валюта")
    payment_url: str = Field(..., description="Ссылка для оплаты")
    payment_reference: str = Field(..., description="Номер платежа")
    expires_at: datetime = Field(..., description="Истечение ссылки")


class BookingNotification(BaseModel):
    """Уведомление о бронировании."""
    booking_id: UUID = Field(..., description="ID бронирования")
    type: str = Field(..., description="Тип уведомления")
    recipient_id: UUID = Field(..., description="ID получателя")
    title: str = Field(..., description="Заголовок")
    message: str = Field(..., description="Сообщение")
    scheduled_at: datetime = Field(..., description="Время отправки")


class BookingConflict(BaseModel):
    """Конфликт бронирования."""
    booking_id: UUID = Field(..., description="ID бронирования")
    conflict_type: str = Field(..., description="Тип конфликта")
    description: str = Field(..., description="Описание конфликта")
    suggested_action: str = Field(..., description="Рекомендуемое действие")


# Схемы для календарной интеграции

class CalendarEvent(BaseModel):
    """Событие календаря."""
    title: str = Field(..., description="Название события")
    description: str = Field(..., description="Описание")
    starts_at: datetime = Field(..., description="Время начала")
    ends_at: datetime = Field(..., description="Время окончания")
    attendees: List[str] = Field(..., description="Email участников")
    location: Optional[str] = Field(None, description="Место проведения")


class CalendarEventResponse(BaseModel):
    """Ответ с событием календаря."""
    event_id: str = Field(..., description="ID события в календаре")
    event_url: str = Field(..., description="Ссылка на событие")
    meet_link: Optional[str] = Field(None, description="Ссылка на Google Meet")


# Схемы для административной панели

class BookingModerationQueue(BaseModel):
    """Очередь модерации бронирований."""
    awaiting_payment: List[BookingResponse] = Field(..., description="Ожидают подтверждения оплаты")
    recent_payments: List[BookingResponse] = Field(..., description="Недавние платежи")
    upcoming_sessions: List[BookingResponse] = Field(..., description="Предстоящие сессии")
    requires_attention: List[BookingConflict] = Field(..., description="Требуют внимания")


class AdminBookingAction(BaseModel):
    """Административное действие с бронированием."""
    action: str = Field(..., description="Действие (confirm, reject, cancel, reschedule)")
    reason: Optional[str] = Field(None, description="Причина действия")
    new_starts_at: Optional[datetime] = Field(None, description="Новое время (для переноса)")
    send_notification: bool = Field(True, description="Отправить уведомление")
    admin_notes: Optional[str] = Field(None, description="Заметки администратора")


class BookingAnalytics(BaseModel):
    """Аналитика бронирований."""
    period: str = Field(..., description="Период (day, week, month)")
    bookings_count: int = Field(..., description="Количество бронирований")
    revenue: Decimal = Field(..., description="Выручка")
    conversion_rate: float = Field(..., description="Конверсия из холда в подтверждение")
    average_lead_time: float = Field(..., description="Среднее время до консультации (дни)")
    popular_durations: Dict[int, int] = Field(..., description="Популярные длительности")
    peak_hours: Dict[int, int] = Field(..., description="Пиковые часы бронирования")


# Схемы для интеграций

class WebhookPayload(BaseModel):
    """Payload для webhook."""
    event_type: str = Field(..., description="Тип события")
    booking_id: UUID = Field(..., description="ID бронирования")
    data: Dict[str, Any] = Field(..., description="Данные события")
    timestamp: datetime = Field(..., description="Время события")

