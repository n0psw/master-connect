"""
Сервисы для модуля доступности.
"""
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Optional, Tuple
from uuid import UUID
import pytz

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from modules.availability.domain.models import AvailabilityRule, TimeOff, MentorSettings
from modules.availability.domain.schemas import (
    AvailabilityCalendar,
    AvailabilityConflicts,
    AvailabilityRuleCreate,
    AvailabilityRuleResponse,
    AvailabilityRuleUpdate,
    AvailabilityStats,
    BulkAvailabilityUpdate,
    ConflictingSlot,
    MentorAvailabilityProfile,
    MentorSettingsResponse,
    MentorSettingsUpdate,
    TimeOffCreate,
    TimeOffResponse,
    TimeOffUpdate,
    TimeSlot,
    WeeklyScheduleResponse,
)
from modules.mentors.domain.models import Mentor
from modules.users.domain.models import User
from modules.bookings.domain.models import Booking, BookingStatus

logger = get_logger(__name__)

_calendar_cache = {}
_cache_ttl = {}


def _invalidate_calendar_cache(mentor_id: UUID) -> None:
    """Сбрасываем кэш календаря для конкретного ментора."""
    global _calendar_cache, _cache_ttl
    keys_to_remove = [k for k in _calendar_cache.keys() if str(mentor_id) in k]
    for key in keys_to_remove:
        _calendar_cache.pop(key, None)
        _cache_ttl.pop(key, None)
    if keys_to_remove:
        logger.info(
            "Cache invalidated for mentor",
            mentor_id=mentor_id,
            keys_removed=len(keys_to_remove)
        )


def _get_calendar_cache_key(mentor_id: UUID, date_from: date, date_to: date, duration_minutes: Optional[int], timezone_str: str) -> str:
    """Генерация ключа кэша для календаря."""
    return f"calendar:{mentor_id}:{date_from}:{date_to}:{duration_minutes}:{timezone_str}"


class AvailabilityService:
    """Сервис для управления доступностью менторов."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_mentor_availability_profile(self, mentor_id: UUID) -> MentorAvailabilityProfile:
        """Получение полного профиля доступности ментора."""
        await self._check_mentor_exists(mentor_id)
        
        # Получаем User напрямую по ID
        user_query = select(User).where(User.id == mentor_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", str(mentor_id))
        
        # Получаем или создаем MentorSettings
        settings_query = select(
            MentorSettings.mentor_id,
            MentorSettings.timezone,
            MentorSettings.buffer_time_minutes,
            MentorSettings.max_bookings_per_day,
            MentorSettings.advance_booking_days,
            MentorSettings.created_at,
            MentorSettings.updated_at
        ).where(MentorSettings.mentor_id == mentor_id)
        settings_result = await self.db.execute(settings_query)
        settings_row = settings_result.first()
        
        if not settings_row:
            # Создаем дефолтные настройки
            new_settings = MentorSettings(
                mentor_id=mentor_id,
                timezone=user.timezone or "UTC",
                buffer_time_minutes=15,
                max_bookings_per_day=8,
                advance_booking_days=30
            )
            self.db.add(new_settings)
            await self.db.commit()
            await self.db.refresh(new_settings)
            
            settings_dict = {
                "mentor_id": new_settings.mentor_id,
                "timezone": new_settings.timezone,
                "buffer_time_minutes": new_settings.buffer_time_minutes,
                "max_bookings_per_day": new_settings.max_bookings_per_day,
                "advance_booking_days": new_settings.advance_booking_days,
                "created_at": new_settings.created_at,
                "updated_at": new_settings.updated_at,
            }
        else:
            settings_dict = {
                "mentor_id": settings_row.mentor_id,
                "timezone": settings_row.timezone,
                "buffer_time_minutes": settings_row.buffer_time_minutes,
                "max_bookings_per_day": settings_row.max_bookings_per_day,
                "advance_booking_days": settings_row.advance_booking_days,
                "created_at": settings_row.created_at,
                "updated_at": settings_row.updated_at,
            }
        
        # Получаем правила доступности
        rules_query = select(AvailabilityRule).where(
            AvailabilityRule.mentor_id == mentor_id
        ).order_by(AvailabilityRule.weekday, AvailabilityRule.time_start)
        
        rules_result = await self.db.execute(rules_query)
        rules = rules_result.scalars().all()
        
        # Преобразуем rules в WeeklyScheduleResponse
        weekly_schedule = self._rules_to_simple_weekly_schedule(rules)
        
        # Получаем периоды отсутствия (только будущие и текущие)
        now = datetime.now(timezone.utc)
        time_offs_query = select(TimeOff).where(
            and_(
                TimeOff.mentor_id == mentor_id,
                TimeOff.ends_at >= now
            )
        ).order_by(TimeOff.starts_at)
        
        time_offs_result = await self.db.execute(time_offs_query)
        time_offs = time_offs_result.scalars().all()
        
        return MentorAvailabilityProfile(
            mentor_id=mentor_id,
            settings=MentorSettingsResponse.model_validate(settings_dict),
            weekly_schedule=weekly_schedule,
            time_offs=[TimeOffResponse.model_validate(time_off, from_attributes=True) for time_off in time_offs]
        )

    async def update_mentor_settings(self, mentor_id: UUID, settings_update: MentorSettingsUpdate) -> MentorSettingsResponse:
        """Обновление (или создание) настроек ментора."""
        await self._check_mentor_exists(mentor_id)

        # Получаем текущие настройки или создаем новые
        query = select(MentorSettings).where(MentorSettings.mentor_id == mentor_id)
        result = await self.db.execute(query)
        settings = result.scalar_one_or_none()

        if settings is None:
            settings = MentorSettings(
                mentor_id=mentor_id,
                timezone=settings_update.timezone or "UTC",
                buffer_time_minutes=settings_update.buffer_time_minutes or 15,
                max_bookings_per_day=settings_update.max_bookings_per_day or 8,
                advance_booking_days=settings_update.advance_booking_days or 30,
            )
            self.db.add(settings)
        else:
            if settings_update.timezone is not None:
                settings.timezone = settings_update.timezone
            if settings_update.buffer_time_minutes is not None:
                settings.buffer_time_minutes = settings_update.buffer_time_minutes
            if settings_update.max_bookings_per_day is not None:
                settings.max_bookings_per_day = settings_update.max_bookings_per_day
            if settings_update.advance_booking_days is not None:
                settings.advance_booking_days = settings_update.advance_booking_days

        await self.db.commit()
        _invalidate_calendar_cache(mentor_id)
        
        settings_query = select(
            MentorSettings.mentor_id,
            MentorSettings.timezone,
            MentorSettings.buffer_time_minutes,
            MentorSettings.max_bookings_per_day,
            MentorSettings.advance_booking_days,
            MentorSettings.created_at,
            MentorSettings.updated_at
        ).where(MentorSettings.mentor_id == mentor_id)
        settings_result = await self.db.execute(settings_query)
        settings_row = settings_result.first()
        
        settings_dict = {
            "mentor_id": settings_row.mentor_id,
            "timezone": settings_row.timezone,
            "buffer_time_minutes": settings_row.buffer_time_minutes,
            "max_bookings_per_day": settings_row.max_bookings_per_day,
            "advance_booking_days": settings_row.advance_booking_days,
            "created_at": settings_row.created_at,
            "updated_at": settings_row.updated_at,
        }
        
        return MentorSettingsResponse.model_validate(settings_dict)

    async def update_weekly_schedule(self, mentor_id: UUID, schedule_data: dict) -> WeeklyScheduleResponse:
        """Полная замена недельного расписания по простому payload из UI.

        Ожидаемый формат schedule_data:
        {
          "monday": [{"start_time": "08:00", "end_time": "12:00"}, ...],
          ...
        }
        """
        await self._check_mentor_exists(mentor_id)

        # Получаем настройки для буфера
        settings_q = select(MentorSettings).where(MentorSettings.mentor_id == mentor_id)
        settings_r = await self.db.execute(settings_q)
        settings = settings_r.scalar_one_or_none()
        buffer_minutes = settings.buffer_time_minutes if settings else 15

        # Удаляем старые правила
        await self.db.execute(delete(AvailabilityRule).where(AvailabilityRule.mentor_id == mentor_id))

        weekday_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        for day_name, intervals in (schedule_data or {}).items():
            if day_name not in weekday_map:
                continue
            weekday = weekday_map[day_name]
            if not isinstance(intervals, list):
                continue
            for it in intervals:
                start_str = it.get("start_time") or it.get("start")
                end_str = it.get("end_time") or it.get("end")
                if not start_str or not end_str:
                    continue
                # Валидация и преобразование
                try:
                    _start = time.fromisoformat(start_str)
                    _end = time.fromisoformat(end_str)
                except ValueError:
                    raise BusinessLogicError("Неверный формат времени, ожидается HH:MM")
                if _end <= _start:
                    raise BusinessLogicError("Время окончания должно быть позже времени начала")

                # Создаем одно универсальное правило
                # slot_duration_minutes=30 - это дефолтное значение, но система гибкая:
                # При запросе календаря можно указать любую длительность (30/45/60 мин),
                # и слоты будут сгенерированы с этой длительностью независимо от slot_duration_minutes
                rule = AvailabilityRule(
                    mentor_id=mentor_id,
                    weekday=weekday,
                    time_start=_start,
                    time_end=_end,
                    slot_duration_minutes=30,
                    buffer_minutes=buffer_minutes,
                    breaks_json=[],
                )
                self.db.add(rule)
                
                logger.info(
                    "Creating availability rule",
                    mentor_id=mentor_id,
                    weekday=weekday,
                    day_name=day_name,
                    time_start=_start.strftime("%H:%M"),
                    time_end=_end.strftime("%H:%M")
                )

        await self.db.commit()
        
        # Очищаем кэш календаря для этого ментора
        global _calendar_cache, _cache_ttl
        keys_to_remove = [k for k in _calendar_cache.keys() if str(mentor_id) in k]
        for key in keys_to_remove:
            _calendar_cache.pop(key, None)
            _cache_ttl.pop(key, None)
        
        logger.info(
            "Cache invalidated for mentor",
            mentor_id=mentor_id,
            keys_removed=len(keys_to_remove)
        )

        # Возвращаем текущее представление расписания
        rules_q = select(AvailabilityRule).where(AvailabilityRule.mentor_id == mentor_id).order_by(
            AvailabilityRule.weekday, AvailabilityRule.time_start
        )
        rules_res = await self.db.execute(rules_q)
        rules = rules_res.scalars().all()
        
        logger.info(
            "Weekly schedule updated",
            mentor_id=mentor_id,
            rules_created=len(rules)
        )
        _invalidate_calendar_cache(mentor_id)

        return self._rules_to_simple_weekly_schedule(rules)
    
    async def create_availability_rule(
        self, 
        mentor_id: UUID, 
        rule_data: AvailabilityRuleCreate
    ) -> AvailabilityRuleResponse:
        """Создание правила доступности."""
        await self._check_mentor_exists(mentor_id)
        
        # Проверяем на конфликты с существующими правилами
        await self._check_rule_conflicts(mentor_id, rule_data, exclude_rule_id=None)
        
        # Преобразуем время в объекты time
        time_start = time.fromisoformat(rule_data.time_start)
        time_end = time.fromisoformat(rule_data.time_end)
        
        # Преобразуем перерывы в JSON
        breaks_json = [break_period.dict() for break_period in rule_data.breaks]
        
        rule = AvailabilityRule(
            mentor_id=mentor_id,
            weekday=rule_data.weekday,
            time_start=time_start,
            time_end=time_end,
            slot_duration_minutes=rule_data.slot_duration_minutes,
            buffer_minutes=rule_data.buffer_minutes,
            breaks_json=breaks_json
        )
        
        self.db.add(rule)
        await self.db.commit()
        _invalidate_calendar_cache(mentor_id)
        
        logger.info(
            "Availability rule created",
            mentor_id=mentor_id,
            weekday=rule_data.weekday,
            time_range=f"{rule_data.time_start}-{rule_data.time_end}"
        )
        
        return AvailabilityRuleResponse.model_validate(rule, from_attributes=True)
    
    async def update_availability_rule(
        self,
        rule_id: UUID,
        rule_data: AvailabilityRuleUpdate
    ) -> AvailabilityRuleResponse:
        """Обновление правила доступности."""
        rule = await self._get_rule_or_404(rule_id)
        
        # Проверяем на конфликты если изменяются ключевые поля
        update_data = rule_data.dict(exclude_unset=True)
        if any(field in update_data for field in ['weekday', 'time_start', 'time_end']):
            # Создаем временное правило для проверки конфликтов
            temp_rule_data = AvailabilityRuleCreate(
                weekday=update_data.get('weekday', rule.weekday),
                time_start=update_data.get('time_start', rule.time_start.strftime('%H:%M')),
                time_end=update_data.get('time_end', rule.time_end.strftime('%H:%M')),
                slot_duration_minutes=update_data.get('slot_duration_minutes', rule.slot_duration_minutes),
                buffer_minutes=update_data.get('buffer_minutes', rule.buffer_minutes),
                breaks=rule_data.breaks if rule_data.breaks is not None else rule.breaks
            )
            await self._check_rule_conflicts(rule.mentor_id, temp_rule_data, exclude_rule_id=rule_id)
        
        # Обновляем поля
        for field, value in update_data.items():
            if field in ['time_start', 'time_end'] and value:
                value = time.fromisoformat(value)
            elif field == 'breaks' and value is not None:
                value = [break_period.dict() for break_period in value]
                field = 'breaks_json'
            
            setattr(rule, field, value)
        
        rule.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        _invalidate_calendar_cache(rule.mentor_id)
        
        logger.info("Availability rule updated", rule_id=rule_id, mentor_id=rule.mentor_id)
        
        return AvailabilityRuleResponse.model_validate(rule, from_attributes=True)
    
    async def delete_availability_rule(self, rule_id: UUID) -> bool:
        """Удаление правила доступности."""
        rule = await self._get_rule_or_404(rule_id)
        
        await self.db.delete(rule)
        await self.db.commit()
        _invalidate_calendar_cache(rule.mentor_id)
        
        logger.info("Availability rule deleted", rule_id=rule_id, mentor_id=rule.mentor_id)
        return True
    
    async def bulk_update_availability(
        self,
        mentor_id: UUID,
        bulk_data: BulkAvailabilityUpdate
    ) -> List[AvailabilityRuleResponse]:
        """Массовое обновление доступности."""
        await self._check_mentor_exists(mentor_id)
        
        if bulk_data.replace_existing:
            # Удаляем все существующие правила
            delete_query = delete(AvailabilityRule).where(
                AvailabilityRule.mentor_id == mentor_id
            )
            await self.db.execute(delete_query)
        
        # Создаем новые правила
        created_rules = []
        for rule_data in bulk_data.rules:
            # Проверяем на конфликты только с уже добавленными правилами в этой операции
            self._check_internal_conflicts(created_rules, rule_data)
            
            time_start = time.fromisoformat(rule_data.time_start)
            time_end = time.fromisoformat(rule_data.time_end)
            breaks_json = [break_period.dict() for break_period in rule_data.breaks]
            
            rule = AvailabilityRule(
                mentor_id=mentor_id,
                weekday=rule_data.weekday,
                time_start=time_start,
                time_end=time_end,
                slot_duration_minutes=rule_data.slot_duration_minutes,
                buffer_minutes=rule_data.buffer_minutes,
                breaks_json=breaks_json
            )
            
            self.db.add(rule)
            created_rules.append(rule)
        
        await self.db.commit()
        _invalidate_calendar_cache(mentor_id)
        
        logger.info(
            "Bulk availability update completed",
            mentor_id=mentor_id,
            rules_count=len(created_rules),
            replace_existing=bulk_data.replace_existing
        )
        
        return [AvailabilityRuleResponse.model_validate(rule) for rule in created_rules]
    
    async def create_time_off(
        self,
        mentor_id: UUID,
        time_off_data: TimeOffCreate
    ) -> TimeOffResponse:
        """Создание периода отсутствия."""
        await self._check_mentor_exists(mentor_id)
        
        # Проверяем пересечения с существующими периодами отсутствия
        await self._check_time_off_conflicts(mentor_id, time_off_data)
        
        time_off = TimeOff(
            mentor_id=mentor_id,
            starts_at=time_off_data.starts_at,
            ends_at=time_off_data.ends_at,
            reason=time_off_data.reason
        )
        
        self.db.add(time_off)
        await self.db.commit()
        _invalidate_calendar_cache(mentor_id)
        
        logger.info(
            "Time off created",
            mentor_id=mentor_id,
            period=f"{time_off_data.starts_at} - {time_off_data.ends_at}",
            reason=time_off_data.reason
        )
        
        return TimeOffResponse.model_validate(time_off, from_attributes=True)
    
    async def update_time_off(
        self,
        time_off_id: UUID,
        time_off_data: TimeOffUpdate
    ) -> TimeOffResponse:
        """Обновление периода отсутствия."""
        time_off = await self._get_time_off_or_404(time_off_id)
        
        # Обновляем поля
        update_data = time_off_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(time_off, field, value)
        
        # Проверяем валидность обновленного периода
        if time_off.ends_at <= time_off.starts_at:
            raise BusinessLogicError("Дата окончания должна быть позже даты начала")
        
        time_off.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        _invalidate_calendar_cache(time_off.mentor_id)
        
        logger.info("Time off updated", time_off_id=time_off_id, mentor_id=time_off.mentor_id)
        
        return TimeOffResponse.model_validate(time_off, from_attributes=True)
    
    async def delete_time_off(self, time_off_id: UUID) -> bool:
        """Удаление периода отсутствия."""
        time_off = await self._get_time_off_or_404(time_off_id)
        
        await self.db.delete(time_off)
        await self.db.commit()
        _invalidate_calendar_cache(time_off.mentor_id)
        
        logger.info("Time off deleted", time_off_id=time_off_id, mentor_id=time_off.mentor_id)
        return True
    
    async def generate_availability_calendar(
        self,
        mentor_id: UUID,
        date_from: date,
        date_to: date,
        duration_minutes: Optional[int] = None,
        timezone_str: str = "Etc/GMT-5"
    ) -> AvailabilityCalendar:
        """Генерация календаря доступности с временными слотами."""
        
        await self._check_mentor_exists(mentor_id)
        
        # Получаем настройки ментора для определения его timezone
        settings_query = select(MentorSettings).where(MentorSettings.mentor_id == mentor_id)
        settings_result = await self.db.execute(settings_query)
        mentor_settings = settings_result.scalar_one_or_none()
        
        # Используем timezone МЕНТОРА, а не студента
        mentor_timezone = mentor_settings.timezone if mentor_settings and mentor_settings.timezone else "Etc/GMT-5"
        
        cache_key = _get_calendar_cache_key(mentor_id, date_from, date_to, duration_minutes, mentor_timezone)
        now = datetime.now(timezone.utc)
        
        if cache_key in _calendar_cache:
            cache_expiry = _cache_ttl.get(cache_key)
            if cache_expiry and now < cache_expiry:
                logger.debug("Returning cached availability calendar", cache_key=cache_key)
                return _calendar_cache[cache_key]
        
        # Получаем правила доступности
        rules_query = select(AvailabilityRule).where(
            AvailabilityRule.mentor_id == mentor_id
        )
        rules_result = await self.db.execute(rules_query)
        rules = rules_result.scalars().all()
        
        if not rules:
            logger.warning(
                "No availability rules found for mentor",
                mentor_id=mentor_id,
                date_from=date_from,
                date_to=date_to
            )
            return AvailabilityCalendar(
                mentor_id=mentor_id,
                date_from=date_from.isoformat(),
                date_to=date_to.isoformat(),
                timezone=mentor_timezone,
                slots=[]
            )
        
        # Получаем периоды отсутствия
        time_offs_query = select(TimeOff).where(
            and_(
                TimeOff.mentor_id == mentor_id,
                TimeOff.starts_at <= datetime.combine(date_to, time.max),
                TimeOff.ends_at >= datetime.combine(date_from, time.min)
            )
        )
        time_offs_result = await self.db.execute(time_offs_query)
        time_offs = time_offs_result.scalars().all()
        
        # Получаем профиль ментора для цен
        mentor_query = select(Mentor).where(Mentor.user_id == mentor_id)
        mentor_result = await self.db.execute(mentor_query)
        mentor = mentor_result.scalar_one_or_none()
        
        # Получаем существующие бронирования
        booked_slots = await self._get_booked_slots(mentor_id, date_from, date_to)
        
        # Генерируем слоты в timezone МЕНТОРА
        slots = self._generate_time_slots(
            rules=rules,
            time_offs=time_offs,
            booked_slots=booked_slots,
            date_from=date_from,
            date_to=date_to,
            duration_filter=duration_minutes,
            timezone_str=mentor_timezone,
            mentor=mentor
        )
        
        logger.info(
            "Availability calendar generated",
            mentor_id=mentor_id,
            mentor_timezone=mentor_timezone,
            date_range=f"{date_from} - {date_to}",
            slots_count=len(slots)
        )
        
        result = AvailabilityCalendar(
            mentor_id=mentor_id,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            timezone=mentor_timezone,
            slots=slots
        )
        
        _calendar_cache[cache_key] = result
        _cache_ttl[cache_key] = now + timedelta(seconds=60)
        
        if len(_calendar_cache) > 1000:
            _calendar_cache.clear()
            _cache_ttl.clear()
            logger.warning("Calendar cache cleared due to size limit")
        
        return result
    
    async def get_availability_conflicts(
        self,
        mentor_id: UUID,
        date_from: date,
        date_to: date
    ) -> AvailabilityConflicts:
        """Получение конфликтов в доступности."""
        conflicts = []
        
        # TODO: Реализовать поиск конфликтов
        # - Пересекающиеся правила доступности
        # - Конфликты с бронированиями
        # - Некорректные периоды отсутствия
        
        return AvailabilityConflicts(
            mentor_id=mentor_id,
            conflicts=conflicts
        )
    
    async def get_availability_stats(self, mentor_id: UUID) -> AvailabilityStats:
        """Получение статистики доступности."""
        await self._check_mentor_exists(mentor_id)
        
        # Определяем даты текущей и следующей недели
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        this_week_end = week_start + timedelta(days=6)
        next_week_start = this_week_end + timedelta(days=1)
        next_week_end = next_week_start + timedelta(days=6)
        
        # Генерируем календарь для двух недель
        this_week_calendar = await self.generate_availability_calendar(
            mentor_id, week_start, this_week_end
        )
        next_week_calendar = await self.generate_availability_calendar(
            mentor_id, next_week_start, next_week_end
        )
        
        # Подсчитываем статистику
        this_week_slots = this_week_calendar.slots
        next_week_slots = next_week_calendar.slots
        
        this_week_available = len([s for s in this_week_slots if s.is_available])
        this_week_booked = len(this_week_slots) - this_week_available
        
        next_week_available = len([s for s in next_week_slots if s.is_available])
        
        # Средний процент бронирований (заглушка)
        average_booking_rate = (this_week_booked / len(this_week_slots) * 100) if this_week_slots else 0
        
        return AvailabilityStats(
            mentor_id=mentor_id,
            total_slots_this_week=len(this_week_slots),
            available_slots_this_week=this_week_available,
            booked_slots_this_week=this_week_booked,
            total_slots_next_week=len(next_week_slots),
            available_slots_next_week=next_week_available,
            average_booking_rate=round(average_booking_rate, 2)
        )
    
    def _generate_time_slots(
        self,
        rules: List[AvailabilityRule],
        time_offs: List[TimeOff],
        booked_slots: List[dict],
        date_from: date,
        date_to: date,
        duration_filter: Optional[int],
        timezone_str: str,
            mentor: Optional[Mentor] = None
        ) -> List[TimeSlot]:
        """Генерация временных слотов на основе правил доступности."""
        slots = []
        # Обработка невалидного timezone с fallback на UTC
        try:
            tz = pytz.timezone(timezone_str) if timezone_str else pytz.UTC
        except (pytz.UnknownTimeZoneError, AttributeError, TypeError):
            logger.warning(
                "Invalid timezone provided, using UTC",
                timezone=timezone_str,
                fallback="UTC"
            )
            tz = pytz.UTC
        current_date = date_from
        
        # Группируем правила по уникальным комбинациям (weekday, time_start, time_end)
        # Это предотвращает дублирование слотов если в БД есть несколько правил для одного интервала
        rules_by_weekday_and_time = {}
        for rule in rules:
            key = (rule.weekday, rule.time_start, rule.time_end)
            if key not in rules_by_weekday_and_time:
                rules_by_weekday_and_time[key] = rule
        
        logger.info(
            "Generating time slots",
            rules_count=len(rules),
            unique_rules_count=len(rules_by_weekday_and_time),
            date_range=f"{date_from} - {date_to}",
            duration_filter=duration_filter,
            timezone_str=timezone_str
        )
        
        while current_date <= date_to:
            weekday = current_date.weekday()
            
            for (rule_weekday, time_start, time_end), rule in rules_by_weekday_and_time.items():
                if rule_weekday == weekday:
                    # Генерируем слоты с запрошенной длительностью
                    day_slots = self._generate_slots_for_rule(
                        rule=rule,
                        target_date=current_date,
                        time_offs=time_offs,
                        booked_slots=booked_slots,
                        timezone=tz,
                        mentor=mentor,
                        requested_duration=duration_filter
                    )
                    slots.extend(day_slots)
            
            current_date += timedelta(days=1)
        
        logger.info(
            "Time slots generated",
            total_slots=len(slots),
            available_slots=len([s for s in slots if s.is_available])
        )
        
        return sorted(slots, key=lambda x: x.start)
    
    def _generate_slots_for_rule(
        self,
        rule: AvailabilityRule,
        target_date: date,
        time_offs: List[TimeOff],
        booked_slots: List[dict],
        timezone: pytz.BaseTzInfo,
        mentor: Optional[Mentor] = None,
        requested_duration: Optional[int] = None
    ) -> List[TimeSlot]:
        """Генерация слотов для конкретного правила на конкретную дату."""
        slots = []
        
        # Создаем datetime объекты для начала и конца рабочего дня
        work_start = datetime.combine(target_date, rule.time_start)
        work_end = datetime.combine(target_date, rule.time_end)
        
        # Локализуем время
        work_start = timezone.localize(work_start)
        work_end = timezone.localize(work_end)
        
        current_time = work_start
        # Используем запрошенную длительность если указана, иначе длительность правила
        actual_duration = requested_duration if requested_duration else rule.slot_duration_minutes
        slot_duration = timedelta(minutes=actual_duration)
        buffer_duration = timedelta(minutes=rule.buffer_minutes)
        
        logger.debug(
            "Generating slots for rule",
            weekday=rule.weekday,
            target_date=target_date.isoformat(),
            time_range=f"{rule.time_start} - {rule.time_end}",
            rule_slot_duration=rule.slot_duration_minutes,
            requested_duration=requested_duration,
            actual_duration=actual_duration,
            buffer_minutes=rule.buffer_minutes
        )
        
        while current_time + slot_duration <= work_end:
            slot_end = current_time + slot_duration
            
            # Проверяем, не попадает ли слот в перерыв
            is_in_break = self._is_time_in_break(current_time.time(), rule.breaks)
            
            # Проверяем, не попадает ли слот в период отсутствия
            is_in_time_off = self._is_slot_in_time_off(current_time, slot_end, time_offs)
            
            # Проверяем, не забронирован ли слот (с учётом буфера между консультациями)
            is_booked = self._is_slot_booked(current_time, slot_end, booked_slots, rule.buffer_minutes)
            
            # Определяем цену на основе запрошенной длительности
            price = self._get_slot_price(actual_duration, mentor)
            
            # Слот доступен если не в перерыве, не в отсутствии и не забронирован
            is_available = not (is_in_break or is_in_time_off or is_booked)
            
            slot = TimeSlot(
                start=current_time.astimezone(pytz.UTC),  # Конвертируем в UTC
                end=slot_end.astimezone(pytz.UTC),
                duration_minutes=actual_duration,
                is_available=is_available,
                price=price
            )
            
            slots.append(slot)
            
            # Переходим к следующему слоту с учетом буфера
            current_time = slot_end + buffer_duration
        
        return slots
    
    def _is_time_in_break(self, slot_time: time, breaks: List[dict]) -> bool:
        """Проверка, попадает ли время в перерыв."""
        for break_info in breaks:
            break_start = time.fromisoformat(break_info['start'])
            break_end = time.fromisoformat(break_info['end'])
            
            if break_start <= slot_time < break_end:
                return True
        
        return False
    
    async def _get_booked_slots(
        self,
        mentor_id: UUID,
        date_from: date,
        date_to: date
    ) -> List[dict]:
        """Получение забронированных слотов ментора."""
        from core.config import settings
        
        now = datetime.now(timezone.utc)
        hold_duration = getattr(settings, 'BOOKING_HOLD_DURATION_MINUTES', 30)
        hold_expiry_threshold = now - timedelta(minutes=hold_duration)
        
        logger.info(
            "Getting booked slots",
            mentor_id=mentor_id,
            now_utc=now.isoformat(),
            hold_duration_minutes=hold_duration,
            hold_expiry_threshold=hold_expiry_threshold.isoformat()
        )
        
        bookings_query = select(Booking).where(
            and_(
                Booking.mentor_id == mentor_id,
                or_(
                    Booking.status.in_([
                        BookingStatus.AWAITING_VERIFICATION,
                        BookingStatus.AWAITING_VERIFICATION.value,
                        BookingStatus.CONFIRMED,
                        BookingStatus.CONFIRMED.value,
                        BookingStatus.COMPLETED,
                        BookingStatus.COMPLETED.value
                    ]),
                    and_(
                        or_(
                            Booking.status == BookingStatus.HOLD,
                            Booking.status == BookingStatus.HOLD.value
                        ),
                        Booking.created_at > hold_expiry_threshold
                    )
                ),
                Booking.starts_at >= datetime.combine(date_from, time.min).replace(tzinfo=timezone.utc),
                Booking.starts_at < datetime.combine(date_to + timedelta(days=1), time.min).replace(tzinfo=timezone.utc)
            )
        )
        
        bookings_result = await self.db.execute(bookings_query)
        bookings = bookings_result.scalars().all()
        
        # Преобразуем в список словарей с временными интервалами
        booked_slots = []
        for booking in bookings:
            start = booking.starts_at
            end = booking.ends_at
            
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            
            status_str = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
            logger.debug(
                "Found booking for slot blocking",
                booking_id=booking.id,
                status=status_str,
                created_at=booking.created_at.isoformat() if booking.created_at else None,
                starts_at=start.isoformat(),
                ends_at=end.isoformat()
            )
            
            booked_slots.append({
                'start': start,
                'end': end,
                'booking_id': booking.id
            })
        
        logger.info(
            "Loaded booked slots for availability check",
            mentor_id=mentor_id,
            date_from=date_from,
            date_to=date_to,
            total_bookings=len(bookings),
            booked_slots=[{
                'start': s['start'].isoformat(),
                'end': s['end'].isoformat(),
                'booking_id': str(s['booking_id'])
            } for s in booked_slots]
        )
        
        return booked_slots
    
    def _is_slot_in_time_off(
        self, 
        slot_start: datetime, 
        slot_end: datetime, 
        time_offs: List[TimeOff]
    ) -> bool:
        """Проверка, попадает ли слот в период отсутствия."""
        for time_off in time_offs:
            time_off_start = time_off.starts_at
            time_off_end = time_off.ends_at
            
            if time_off_start.tzinfo is None:
                time_off_start = time_off_start.replace(tzinfo=timezone.utc)
            if time_off_end.tzinfo is None:
                time_off_end = time_off_end.replace(tzinfo=timezone.utc)
            
            if (slot_start < time_off_end and slot_end > time_off_start):
                return True
        
        return False
    
    def _is_slot_booked(
        self,
        slot_start: datetime,
        slot_end: datetime,
        booked_slots: List[dict],
        buffer_minutes: int = 0
    ) -> bool:
        """Проверка, забронирован ли слот с учётом буфера между консультациями."""
        buffer = timedelta(minutes=buffer_minutes)
        
        for booked_slot in booked_slots:
            booked_start = booked_slot['start']
            booked_end = booked_slot['end']
            
            booked_end_with_buffer = booked_end + buffer
            
            if (slot_start < booked_end_with_buffer and slot_end > booked_start):
                logger.debug(
                    "Slot conflicts with booking",
                    slot_start=slot_start,
                    slot_end=slot_end,
                    booked_start=booked_start,
                    booked_end=booked_end,
                    booked_end_with_buffer=booked_end_with_buffer,
                    buffer_minutes=buffer_minutes
                )
                return True
        
        return False
    
    def _get_slot_price(self, duration_minutes: int, mentor: Optional[Mentor] = None) -> Optional[float]:
        """Получение цены за слот в зависимости от длительности."""
        if mentor:
            # Используем цены из профиля ментора
            if duration_minutes == 30 and mentor.price_30:
                return float(mentor.price_30)
            elif duration_minutes == 45 and mentor.price_45:
                return float(mentor.price_45)
            elif duration_minutes == 60 and mentor.price_60:
                return float(mentor.price_60)
        
        # Если цена не указана, используем дефолтные значения
        price_map = {
            30: 15000,  # 30 минут - 15000 тенге
            45: 22500,  # 45 минут - 22500 тенге  
            60: 30000,  # 60 минут - 30000 тенге
        }
        return price_map.get(duration_minutes)
    
    async def _check_mentor_exists(self, mentor_id: UUID) -> None:
        """Проверка существования ментора."""
        mentor_query = select(Mentor).where(Mentor.user_id == mentor_id)
        mentor_result = await self.db.execute(mentor_query)
        mentor = mentor_result.scalar_one_or_none()
        
        if not mentor:
            raise NotFoundError("Mentor", str(mentor_id))
    
    async def _check_rule_conflicts(
        self, 
        mentor_id: UUID, 
        rule_data: AvailabilityRuleCreate,
        exclude_rule_id: Optional[UUID] = None
    ) -> None:
        """Проверка конфликтов с существующими правилами."""
        # Проверяем пересечения по времени в тот же день недели
        query = select(AvailabilityRule).where(
            and_(
                AvailabilityRule.mentor_id == mentor_id,
                AvailabilityRule.weekday == rule_data.weekday
            )
        )
        
        if exclude_rule_id:
            query = query.where(AvailabilityRule.id != exclude_rule_id)
        
        result = await self.db.execute(query)
        existing_rules = result.scalars().all()
        
        new_start = time.fromisoformat(rule_data.time_start)
        new_end = time.fromisoformat(rule_data.time_end)
        
        for existing_rule in existing_rules:
            # Проверяем пересечение временных интервалов
            if (new_start < existing_rule.time_end and new_end > existing_rule.time_start):
                weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                raise BusinessLogicError(
                    f"Конфликт с существующим правилом в {weekday_names[rule_data.weekday]} "
                    f"{existing_rule.time_start}-{existing_rule.time_end}"
                )
    
    def _check_internal_conflicts(
        self, 
        existing_rules: List[AvailabilityRule], 
        new_rule: AvailabilityRuleCreate
    ) -> None:
        """Проверка конфликтов внутри одной операции."""
        new_start = time.fromisoformat(new_rule.time_start)
        new_end = time.fromisoformat(new_rule.time_end)
        
        for rule in existing_rules:
            if rule.weekday == new_rule.weekday:
                if (new_start < rule.time_end and new_end > rule.time_start):
                    weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                    raise BusinessLogicError(
                        f"Конфликт между правилами в {weekday_names[new_rule.weekday]} "
                        f"{new_rule.time_start}-{new_rule.time_end}"
                    )
    
    async def _check_time_off_conflicts(
        self, 
        mentor_id: UUID, 
        time_off_data: TimeOffCreate
    ) -> None:
        """Проверка конфликтов с существующими периодами отсутствия."""
        query = select(TimeOff).where(
            and_(
                TimeOff.mentor_id == mentor_id,
                or_(
                    and_(
                        TimeOff.starts_at <= time_off_data.starts_at,
                        TimeOff.ends_at > time_off_data.starts_at
                    ),
                    and_(
                        TimeOff.starts_at < time_off_data.ends_at,
                        TimeOff.ends_at >= time_off_data.ends_at
                    ),
                    and_(
                        TimeOff.starts_at >= time_off_data.starts_at,
                        TimeOff.ends_at <= time_off_data.ends_at
                    )
                )
            )
        )
        
        result = await self.db.execute(query)
        conflicting_time_off = result.scalar_one_or_none()
        
        if conflicting_time_off:
            raise BusinessLogicError(
                f"Конфликт с существующим периодом отсутствия "
                f"{conflicting_time_off.starts_at} - {conflicting_time_off.ends_at}"
            )
    
    async def _get_rule_or_404(self, rule_id: UUID) -> AvailabilityRule:
        """Получение правила доступности или 404."""
        query = select(AvailabilityRule).where(AvailabilityRule.id == rule_id)
        result = await self.db.execute(query)
        rule = result.scalar_one_or_none()
        
        if not rule:
            raise NotFoundError("AvailabilityRule", str(rule_id))
        
        return rule
    
    async def _get_time_off_or_404(self, time_off_id: UUID) -> TimeOff:
        """Получение периода отсутствия или 404."""
        query = select(TimeOff).where(TimeOff.id == time_off_id)
        result = await self.db.execute(query)
        time_off = result.scalar_one_or_none()
        
        if not time_off:
            raise NotFoundError("TimeOff", str(time_off_id))
        
        return time_off
    
    def _rules_to_weekly_schedule(self, rules: List[AvailabilityRule], timezone_str: str) -> WeeklyScheduleResponse:
        """Преобразование правил доступности в недельное расписание."""
        
        # Обработка невалидного timezone с fallback на UTC
        try:
            tz = pytz.timezone(timezone_str) if timezone_str else pytz.UTC
        except (pytz.UnknownTimeZoneError, AttributeError, TypeError):
            logger.warning(
                "Invalid timezone provided in weekly schedule, using UTC",
                timezone=timezone_str,
                fallback="UTC"
            )
            tz = pytz.UTC
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Группируем правила по дням недели
        rules_by_weekday = {}
        for rule in rules:
            if rule.weekday not in rules_by_weekday:
                rules_by_weekday[rule.weekday] = []
            rules_by_weekday[rule.weekday].append(rule)
        
        # Генерируем слоты для каждого дня недели
        weekday_slots = {i: [] for i in range(7)}
        
        for weekday in range(7):
            if weekday in rules_by_weekday:
                target_date = week_start + timedelta(days=weekday)
                day_rules = rules_by_weekday[weekday]
                
                for rule in day_rules:
                    work_start = datetime.combine(target_date, rule.time_start)
                    work_end = datetime.combine(target_date, rule.time_end)
                    work_start = tz.localize(work_start)
                    work_end = tz.localize(work_end)
                    
                    current_time = work_start
                    slot_duration = timedelta(minutes=rule.slot_duration_minutes)
                    buffer_duration = timedelta(minutes=rule.buffer_minutes)
                    
                    while current_time + slot_duration <= work_end:
                        slot_end = current_time + slot_duration
                        
                        is_in_break = self._is_time_in_break(current_time.time(), rule.breaks)
                        
                        if not is_in_break:
                            slot = TimeSlot(
                                start=current_time.astimezone(pytz.UTC),
                                end=slot_end.astimezone(pytz.UTC),
                                duration_minutes=rule.slot_duration_minutes,
                                is_available=True,
                                price=None
                            )
                            weekday_slots[weekday].append(slot)
                        
                        current_time = slot_end + buffer_duration
        
        return WeeklyScheduleResponse(
            monday=weekday_slots[0],
            tuesday=weekday_slots[1],
            wednesday=weekday_slots[2],
            thursday=weekday_slots[3],
            friday=weekday_slots[4],
            saturday=weekday_slots[5],
            sunday=weekday_slots[6]
        )
    
    def _rules_to_simple_weekly_schedule(self, rules: List[AvailabilityRule]) -> WeeklyScheduleResponse:
        """Преобразование правил в простой формат для UI (без timezone конвертации)."""
        
        rules_by_weekday = {}
        for rule in rules:
            if rule.weekday not in rules_by_weekday:
                rules_by_weekday[rule.weekday] = []
            rules_by_weekday[rule.weekday].append({
                "start_time": rule.time_start.strftime("%H:%M"),
                "end_time": rule.time_end.strftime("%H:%M")
            })
        
        schedule_dict = {
            "monday": rules_by_weekday.get(0, []),
            "tuesday": rules_by_weekday.get(1, []),
            "wednesday": rules_by_weekday.get(2, []),
            "thursday": rules_by_weekday.get(3, []),
            "friday": rules_by_weekday.get(4, []),
            "saturday": rules_by_weekday.get(5, []),
            "sunday": rules_by_weekday.get(6, [])
        }
        
        return WeeklyScheduleResponse(**schedule_dict)

