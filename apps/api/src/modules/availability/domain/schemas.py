"""
Pydantic схемы для модуля доступности.
"""
from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, field_serializer, model_validator, field_validator, computed_field, model_serializer


class BreakPeriod(BaseModel):
    """Период перерыва."""
    start: str = Field(..., description="Время начала перерыва (HH:MM)")
    end: str = Field(..., description="Время окончания перерыва (HH:MM)")
    title: str = Field("Перерыв", description="Название перерыва")
    
    @validator("start", "end")
    def validate_time_format(cls, v):
        """Валидация формата времени."""
        try:
            time.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Время должно быть в формате HH:MM")
    
    @validator("end")
    def validate_end_after_start(cls, v, values):
        """Проверка, что время окончания позже времени начала."""
        start = values.get("start")
        if start and v:
            start_time = time.fromisoformat(start)
            end_time = time.fromisoformat(v)
            if end_time <= start_time:
                raise ValueError("Время окончания должно быть позже времени начала")
        return v


class AvailabilityRuleBase(BaseModel):
    """Базовая схема правила доступности."""
    weekday: int = Field(..., ge=0, le=6, description="День недели (0=пн, 6=вс)")
    time_start: str = Field(..., description="Время начала работы (HH:MM)")
    time_end: str = Field(..., description="Время окончания работы (HH:MM)")
    slot_duration_minutes: int = Field(..., gt=0, le=120, description="Длительность слота в минутах")
    buffer_minutes: int = Field(10, ge=0, le=60, description="Буфер между слотами в минутах")
    breaks: List[BreakPeriod] = Field(default=[], description="Перерывы")
    
    @validator("time_start", "time_end")
    def validate_time_format(cls, v):
        """Валидация формата времени."""
        try:
            time.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Время должно быть в формате HH:MM")
    
    @validator("time_end")
    def validate_end_after_start(cls, v, values):
        """Проверка, что время окончания позже времени начала."""
        time_start = values.get("time_start")
        if time_start and v:
            start = time.fromisoformat(time_start)
            end = time.fromisoformat(v)
            if end <= start:
                raise ValueError("Время окончания должно быть позже времени начала")
        return v
    
    @validator("slot_duration_minutes")
    def validate_slot_duration(cls, v):
        """Валидация длительности слота."""
        if v not in [30, 45, 60]:
            raise ValueError("Длительность слота должна быть 30, 45 или 60 минут")
        return v


class AvailabilityRuleCreate(AvailabilityRuleBase):
    """Схема для создания правила доступности."""
    pass


class AvailabilityRuleUpdate(AvailabilityRuleBase):
    """Схема для обновления правила доступности."""
    weekday: Optional[int] = Field(None, ge=0, le=6, description="День недели (0=пн, 6=вс)")
    time_start: Optional[str] = Field(None, description="Время начала работы (HH:MM)")
    time_end: Optional[str] = Field(None, description="Время окончания работы (HH:MM)")
    slot_duration_minutes: Optional[int] = Field(None, gt=0, le=120, description="Длительность слота в минутах")


class AvailabilityRuleResponse(AvailabilityRuleBase):
    """Схема ответа с правилом доступности."""
    id: UUID = Field(..., description="ID правила")
    mentor_id: UUID = Field(..., description="ID ментора")
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата последнего обновления")
    
    class Config:
        from_attributes = True


class TimeOffBase(BaseModel):
    """Базовая схема отсутствия."""
    starts_at: datetime = Field(..., description="Начало периода отсутствия")
    ends_at: datetime = Field(..., description="Окончание периода отсутствия")
    reason: Optional[str] = Field(None, max_length=255, description="Причина отсутствия")
    
    @validator("ends_at")
    def validate_end_after_start(cls, v, values):
        """Проверка, что дата окончания позже даты начала."""
        starts_at = values.get("starts_at")
        if starts_at and v <= starts_at:
            raise ValueError("Дата окончания должна быть позже даты начала")
        return v


class TimeOffCreate(TimeOffBase):
    """Схема для создания периода отсутствия."""
    pass


class TimeOffUpdate(BaseModel):
    """Схема для обновления периода отсутствия."""
    starts_at: Optional[datetime] = Field(None, description="Начало периода отсутствия")
    ends_at: Optional[datetime] = Field(None, description="Окончание периода отсутствия")
    reason: Optional[str] = Field(None, max_length=255, description="Причина отсутствия")


class TimeOffResponse(TimeOffBase):
    """Схема ответа с периодом отсутствия."""
    id: UUID = Field(..., description="ID периода отсутствия")
    mentor_id: UUID = Field(..., description="ID ментора")
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата последнего обновления")
    
    class Config:
        from_attributes = True


class TimeSlot(BaseModel):
    """Временной слот для бронирования."""
    start: datetime = Field(..., description="Время начала слота")
    end: datetime = Field(..., description="Время окончания слота")
    duration_minutes: int = Field(..., description="Длительность в минутах")
    is_available: bool = Field(..., description="Доступен ли слот для бронирования")
    price: Optional[float] = Field(None, description="Цена за слот")
    
    @field_serializer('start', 'end')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Сериализация datetime в ISO формат строки."""
        if dt.tzinfo is None:
            # Если нет timezone, добавляем UTC
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    
    @computed_field
    @property
    def date(self) -> str:
        """Дата слота в формате YYYY-MM-DD."""
        dt = self.start
        if isinstance(dt, str):
            # Если start уже строка (после сериализации), парсим её
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return dt.date().isoformat()
    
    @computed_field
    @property
    def time(self) -> str:
        """Время начала слота в формате HH:MM."""
        dt = self.start
        if isinstance(dt, str):
            # Если start уже строка (после сериализации), парсим её
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return dt.time().strftime('%H:%M')


class AvailabilityCalendar(BaseModel):
    """Календарь доступности ментора."""
    mentor_id: UUID = Field(..., description="ID ментора")
    date_from: str = Field(..., description="Начальная дата (YYYY-MM-DD)")
    date_to: str = Field(..., description="Конечная дата (YYYY-MM-DD)")
    timezone: str = Field(..., description="Часовой пояс")
    slots: List[TimeSlot] = Field(..., description="Доступные слоты")


class MentorSettingsBase(BaseModel):
    """Базовая схема настроек ментора."""
    timezone: str = Field(..., description="Часовой пояс ментора")
    buffer_time_minutes: int = Field(15, ge=5, le=60, description="Буферное время между консультациями в минутах")
    max_bookings_per_day: int = Field(8, ge=1, le=20, description="Максимальное количество бронирований в день")
    advance_booking_days: int = Field(30, ge=1, le=90, description="За сколько дней вперед можно бронировать")


class MentorSettingsUpdate(BaseModel):
    """Схема для обновления настроек ментора."""
    timezone: Optional[str] = Field(None, description="Часовой пояс ментора")
    buffer_time_minutes: Optional[int] = Field(None, ge=5, le=60, description="Буферное время между консультациями в минутах")
    max_bookings_per_day: Optional[int] = Field(None, ge=1, le=20, description="Максимальное количество бронирований в день")
    advance_booking_days: Optional[int] = Field(None, ge=1, le=90, description="За сколько дней вперед можно бронировать")


class MentorSettingsResponse(MentorSettingsBase):
    """Схема ответа с настройками ментора."""
    mentor_id: UUID = Field(..., description="ID ментора")
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата последнего обновления")
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_string(cls, v):
        """Преобразование datetime в строку ISO формата."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    class Config:
        from_attributes = True


class SimpleTimeSlot(BaseModel):
    """Простой временной слот для UI."""
    start_time: str = Field(..., description="Время начала (HH:MM)")
    end_time: str = Field(..., description="Время окончания (HH:MM)")


class WeeklyScheduleResponse(BaseModel):
    """Схема недельного расписания для Frontend."""
    monday: List[SimpleTimeSlot] = Field(default=[], description="Слоты понедельника")
    tuesday: List[SimpleTimeSlot] = Field(default=[], description="Слоты вторника")
    wednesday: List[SimpleTimeSlot] = Field(default=[], description="Слоты среды")
    thursday: List[SimpleTimeSlot] = Field(default=[], description="Слоты четверга")
    friday: List[SimpleTimeSlot] = Field(default=[], description="Слоты пятницы")
    saturday: List[SimpleTimeSlot] = Field(default=[], description="Слоты субботы")
    sunday: List[SimpleTimeSlot] = Field(default=[], description="Слоты воскресенья")


class MentorAvailabilityProfile(BaseModel):
    """Полный профиль доступности ментора."""
    mentor_id: UUID = Field(..., description="ID ментора")
    settings: MentorSettingsResponse = Field(..., description="Настройки ментора")
    weekly_schedule: WeeklyScheduleResponse = Field(..., description="Недельное расписание")
    time_offs: List[TimeOffResponse] = Field(..., description="Периоды отсутствия")


class WeeklyScheduleUpdate(BaseModel):
    """Схема для обновления недельного расписания."""
    monday: List[TimeSlot] = Field(default=[], description="Слоты понедельника")
    tuesday: List[TimeSlot] = Field(default=[], description="Слоты вторника")
    wednesday: List[TimeSlot] = Field(default=[], description="Слоты среды")
    thursday: List[TimeSlot] = Field(default=[], description="Слоты четверга")
    friday: List[TimeSlot] = Field(default=[], description="Слоты пятницы")
    saturday: List[TimeSlot] = Field(default=[], description="Слоты субботы")
    sunday: List[TimeSlot] = Field(default=[], description="Слоты воскресенья")


class BulkAvailabilityUpdate(BaseModel):
    """Массовое обновление доступности."""
    rules: List[AvailabilityRuleCreate] = Field(..., description="Новые правила доступности")
    replace_existing: bool = Field(False, description="Заменить существующие правила")


class AvailabilityStats(BaseModel):
    """Статистика доступности."""
    mentor_id: UUID = Field(..., description="ID ментора")
    total_slots_this_week: int = Field(..., description="Общее количество слотов на эту неделю")
    available_slots_this_week: int = Field(..., description="Доступных слотов на эту неделю")
    booked_slots_this_week: int = Field(..., description="Забронированных слотов на эту неделю")
    total_slots_next_week: int = Field(..., description="Общее количество слотов на следующую неделю")
    available_slots_next_week: int = Field(..., description="Доступных слотов на следующую неделю")
    average_booking_rate: float = Field(..., description="Средний процент забронированных слотов")


class SlotGenerationRequest(BaseModel):
    """Запрос на генерацию слотов."""
    date_from: str = Field(..., description="Начальная дата (YYYY-MM-DD)")
    date_to: str = Field(..., description="Конечная дата (YYYY-MM-DD)")
    duration_minutes: Optional[int] = Field(None, description="Фильтр по длительности слота")
    timezone: str = Field("UTC", description="Часовой пояс для генерации слотов")


class ConflictingSlot(BaseModel):
    """Информация о конфликтующем слоте."""
    start: datetime = Field(..., description="Время начала конфликта")
    end: datetime = Field(..., description="Время окончания конфликта")
    conflict_type: str = Field(..., description="Тип конфликта (booking, time_off, break)")
    description: str = Field(..., description="Описание конфликта")


class AvailabilityConflicts(BaseModel):
    """Конфликты в доступности."""
    mentor_id: UUID = Field(..., description="ID ментора")
    conflicts: List[ConflictingSlot] = Field(..., description="Список конфликтов")


# Валидационные схемы для фильтров

class WeekdayNames(BaseModel):
    """Названия дней недели."""
    names: Dict[int, str] = Field(
        default={
            0: "Понедельник",
            1: "Вторник", 
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье"
        },
        description="Соответствие номеров дней недели их названиям"
    )


class TimezoneInfo(BaseModel):
    """Информация о часовом поясе."""
    timezone: str = Field(..., description="Идентификатор часового пояса")
    offset: str = Field(..., description="Смещение от UTC (например, +03:00)")
    name: str = Field(..., description="Название часового пояса")


class WorkingHoursTemplate(BaseModel):
    """Шаблон рабочих часов."""
    name: str = Field(..., description="Название шаблона")
    description: str = Field(..., description="Описание шаблона")
    rules: List[AvailabilityRuleCreate] = Field(..., description="Правила доступности")


class PopularWorkingHours(BaseModel):
    """Популярные рабочие часы."""
    templates: List[WorkingHoursTemplate] = Field(..., description="Список популярных шаблонов")
    
    @classmethod
    def get_default_templates(cls) -> "PopularWorkingHours":
        """Получение шаблонов по умолчанию."""
        templates = [
            WorkingHoursTemplate(
                name="Стандартные рабочие часы",
                description="Пн-Пт 9:00-18:00",
                rules=[
                    AvailabilityRuleCreate(
                        weekday=i,
                        time_start="09:00",
                        time_end="18:00",
                        slot_duration_minutes=60,
                        buffer_minutes=10,
                        breaks=[
                            BreakPeriod(start="12:00", end="13:00", title="Обед")
                        ]
                    ) for i in range(5)  # Пн-Пт
                ]
            ),
            WorkingHoursTemplate(
                name="Гибкий график",
                description="Пн-Сб 10:00-22:00 с перерывами",
                rules=[
                    AvailabilityRuleCreate(
                        weekday=i,
                        time_start="10:00",
                        time_end="22:00",
                        slot_duration_minutes=45,
                        buffer_minutes=15,
                        breaks=[
                            BreakPeriod(start="13:00", end="14:00", title="Обед"),
                            BreakPeriod(start="19:00", end="20:00", title="Ужин")
                        ]
                    ) for i in range(6)  # Пн-Сб
                ]
            ),
            WorkingHoursTemplate(
                name="Выходные",
                description="Сб-Вс 12:00-18:00",
                rules=[
                    AvailabilityRuleCreate(
                        weekday=i,
                        time_start="12:00",
                        time_end="18:00",
                        slot_duration_minutes=60,
                        buffer_minutes=10,
                        breaks=[]
                    ) for i in [5, 6]  # Сб-Вс
                ]
            )
        ]
        return cls(templates=templates)

