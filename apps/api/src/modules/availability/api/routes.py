"""
API роуты для модуля доступности.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_active_user,
    get_current_mentor,
    get_current_mentor_or_admin,
    get_current_user_info,
    CurrentUserInfo,
    verify_resource_ownership,
)
from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from core.rbac import Permission
from db.session import get_db
from modules.availability.application.services import AvailabilityService
from modules.availability.domain.schemas import (
    AvailabilityCalendar,
    AvailabilityConflicts,
    AvailabilityRuleCreate,
    AvailabilityRuleResponse,
    AvailabilityRuleUpdate,
    AvailabilityStats,
    BulkAvailabilityUpdate,
    MentorAvailabilityProfile,
    MentorSettingsResponse,
    MentorSettingsUpdate,
    PopularWorkingHours,
    SlotGenerationRequest,
    TimeOffCreate,
    TimeOffResponse,
    TimeOffUpdate,
    TimezoneInfo,
    WeekdayNames,
    WeeklyScheduleResponse,
)
from modules.users.domain.models import User, UserRole

logger = get_logger(__name__)

router = APIRouter(prefix="/availability", tags=["Доступность"])


async def get_availability_service(db: AsyncSession = Depends(get_db)) -> AvailabilityService:
    """Dependency для получения сервиса доступности."""
    return AvailabilityService(db)


# === Публичные endpoints для получения слотов ===

@router.get(
    "/mentors/{mentor_id}/calendar",
    response_model=AvailabilityCalendar,
    summary="Календарь доступности ментора",
    description="Получение календаря доступности ментора с временными слотами",
    responses={
        200: {"description": "Календарь доступности"},
        400: {"description": "Некорректные параметры запроса"},
        404: {"description": "Ментор не найден"},
    }
)
async def get_mentor_availability_calendar(
    mentor_id: UUID,
    date_from: date = Query(..., description="Начальная дата (YYYY-MM-DD)"),
    date_to: date = Query(..., description="Конечная дата (YYYY-MM-DD)"),
    duration_minutes: Optional[int] = Query(None, description="Фильтр по длительности слота"),
    timezone: str = Query("UTC", description="Часовой пояс"),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> AvailabilityCalendar:
    """
    Получение календаря доступности ментора.
    
    Возвращает список временных слотов для бронирования в указанный период.
    """
    if date_to < date_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Конечная дата не может быть раньше начальной"
        )
    
    max_days = (date_to - date_from).days
    if max_days > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Максимальный период запроса - 60 дней"
        )
    
    calendar = await availability_service.generate_availability_calendar(
        mentor_id=mentor_id,
        date_from=date_from,
        date_to=date_to,
        duration_minutes=duration_minutes,
        timezone_str=timezone
    )
    
    return calendar


# === Endpoints для менторов ===

@router.get(
    "/my/profile",
    response_model=MentorAvailabilityProfile,
    summary="Мой профиль доступности",
    description="Получение полного профиля доступности для текущего ментора",
    responses={
        200: {"description": "Профиль доступности"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
    }
)
async def get_my_availability_profile(
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> MentorAvailabilityProfile:
    """Получение профиля доступности текущего ментора."""
    profile = await availability_service.get_mentor_availability_profile(current_user.id)
    return profile


@router.put(
    "/my/settings",
    response_model=MentorSettingsResponse,
    summary="Сохранить настройки доступности",
    description="Обновление (или создание) настроек доступности текущего ментора",
)
async def update_my_settings(
    settings: MentorSettingsUpdate,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> MentorSettingsResponse:
    return await availability_service.update_mentor_settings(current_user.id, settings)


@router.put(
    "/my/schedule",
    response_model=WeeklyScheduleResponse,
    summary="Сохранить недельное расписание",
    description="Полная замена недельного расписания по переданным интервалам (start_time/end_time)",
)
async def update_my_schedule(
    schedule: dict,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> WeeklyScheduleResponse:
    return await availability_service.update_weekly_schedule(current_user.id, schedule)


@router.post(
    "/my/rules",
    response_model=AvailabilityRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать правило доступности",
    description="Создание нового правила доступности для текущего ментора",
    responses={
        201: {"description": "Правило создано"},
        400: {"description": "Конфликт с существующими правилами"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_my_availability_rule(
    rule_data: AvailabilityRuleCreate,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> AvailabilityRuleResponse:
    """Создание правила доступности."""
    rule = await availability_service.create_availability_rule(
        mentor_id=current_user.id,
        rule_data=rule_data
    )
    
    logger.info("Availability rule created by mentor", mentor_id=current_user.id, rule_id=rule.id)
    return rule


@router.put(
    "/my/rules/{rule_id}",
    response_model=AvailabilityRuleResponse,
    summary="Обновить правило доступности",
    description="Обновление существующего правила доступности",
    responses={
        200: {"description": "Правило обновлено"},
        400: {"description": "Конфликт с существующими правилами"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Правило не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_my_availability_rule(
    rule_id: UUID,
    rule_data: AvailabilityRuleUpdate,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> AvailabilityRuleResponse:
    """Обновление правила доступности."""
    rule = await availability_service.update_availability_rule(
        rule_id=rule_id,
        rule_data=rule_data
    )
    
    logger.info("Availability rule updated by mentor", mentor_id=current_user.id, rule_id=rule_id)
    return rule


@router.delete(
    "/my/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить правило доступности",
    description="Удаление правила доступности",
    responses={
        204: {"description": "Правило удалено"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Правило не найдено"},
    }
)
async def delete_my_availability_rule(
    rule_id: UUID,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> None:
    """Удаление правила доступности."""
    await availability_service.delete_availability_rule(rule_id)
    logger.info("Availability rule deleted by mentor", mentor_id=current_user.id, rule_id=rule_id)


@router.put(
    "/my/rules/bulk",
    response_model=List[AvailabilityRuleResponse],
    summary="Массовое обновление доступности",
    description="Массовое создание/обновление правил доступности",
    responses={
        200: {"description": "Правила обновлены"},
        400: {"description": "Конфликты в правилах"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        422: {"description": "Ошибка валидации"},
    }
)
async def bulk_update_my_availability(
    bulk_data: BulkAvailabilityUpdate,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> List[AvailabilityRuleResponse]:
    """Массовое обновление правил доступности."""
    rules = await availability_service.bulk_update_availability(
        mentor_id=current_user.id,
        bulk_data=bulk_data
    )
    
    logger.info(
        "Bulk availability update by mentor", 
        mentor_id=current_user.id, 
        rules_count=len(rules),
        replace_existing=bulk_data.replace_existing
    )
    
    return rules


# === Time Off endpoints ===

@router.post(
    "/my/time-off",
    response_model=TimeOffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать период отсутствия",
    description="Создание периода отсутствия (отпуск, болезнь и т.д.)",
    responses={
        201: {"description": "Период отсутствия создан"},
        400: {"description": "Конфликт с существующими периодами"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_my_time_off(
    time_off_data: TimeOffCreate,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> TimeOffResponse:
    """Создание периода отсутствия."""
    time_off = await availability_service.create_time_off(
        mentor_id=current_user.id,
        time_off_data=time_off_data
    )
    
    logger.info("Time off created by mentor", mentor_id=current_user.id, time_off_id=time_off.id)
    return time_off


@router.put(
    "/my/time-off/{time_off_id}",
    response_model=TimeOffResponse,
    summary="Обновить период отсутствия",
    description="Обновление существующего периода отсутствия",
    responses={
        200: {"description": "Период отсутствия обновлен"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Период отсутствия не найден"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_my_time_off(
    time_off_id: UUID,
    time_off_data: TimeOffUpdate,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> TimeOffResponse:
    """Обновление периода отсутствия."""
    time_off = await availability_service.update_time_off(
        time_off_id=time_off_id,
        time_off_data=time_off_data
    )
    
    logger.info("Time off updated by mentor", mentor_id=current_user.id, time_off_id=time_off_id)
    return time_off


@router.delete(
    "/my/time-off/{time_off_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить период отсутствия",
    description="Удаление периода отсутствия",
    responses={
        204: {"description": "Период отсутствия удален"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
        404: {"description": "Период отсутствия не найден"},
    }
)
async def delete_my_time_off(
    time_off_id: UUID,
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> None:
    """Удаление периода отсутствия."""
    await availability_service.delete_time_off(time_off_id)
    logger.info("Time off deleted by mentor", mentor_id=current_user.id, time_off_id=time_off_id)


# === Статистика и аналитика ===

@router.get(
    "/my/stats",
    response_model=AvailabilityStats,
    summary="Статистика моей доступности",
    description="Получение статистики доступности для текущего ментора",
    responses={
        200: {"description": "Статистика доступности"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
    }
)
async def get_my_availability_stats(
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> AvailabilityStats:
    """Получение статистики доступности текущего ментора."""
    stats = await availability_service.get_availability_stats(current_user.id)
    return stats


@router.get(
    "/my/conflicts",
    response_model=AvailabilityConflicts,
    summary="Конфликты в моей доступности",
    description="Получение информации о конфликтах в доступности",
    responses={
        200: {"description": "Конфликты в доступности"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Доступно только для менторов"},
    }
)
async def get_my_availability_conflicts(
    date_from: date = Query(..., description="Начальная дата для проверки"),
    date_to: date = Query(..., description="Конечная дата для проверки"),
    current_user: User = Depends(get_current_mentor),
    availability_service: AvailabilityService = Depends(get_availability_service)
) -> AvailabilityConflicts:
    """Получение конфликтов в доступности."""
    conflicts = await availability_service.get_availability_conflicts(
        mentor_id=current_user.id,
        date_from=date_from,
        date_to=date_to
    )
    return conflicts


# === Утилитарные endpoints ===

@router.get(
    "/templates/working-hours",
    response_model=PopularWorkingHours,
    summary="Шаблоны рабочих часов",
    description="Получение популярных шаблонов рабочих часов",
    responses={
        200: {"description": "Шаблоны рабочих часов"},
    }
)
async def get_working_hours_templates() -> PopularWorkingHours:
    """Получение шаблонов рабочих часов."""
    return PopularWorkingHours.get_default_templates()


@router.get(
    "/utils/weekdays",
    response_model=WeekdayNames,
    summary="Названия дней недели",
    description="Получение соответствия номеров дней недели их названиям",
    responses={
        200: {"description": "Названия дней недели"},
    }
)
async def get_weekday_names() -> WeekdayNames:
    """Получение названий дней недели."""
    return WeekdayNames()


@router.get(
    "/utils/timezones",
    response_model=List[TimezoneInfo],
    summary="Список часовых поясов",
    description="Получение списка поддерживаемых часовых поясов",
    responses={
        200: {"description": "Список часовых поясов"},
    }
)
async def get_supported_timezones() -> List[TimezoneInfo]:
    """Получение списка поддерживаемых часовых поясов."""
    # Популярные часовые пояса для платформы
    timezones = [
        TimezoneInfo(timezone="UTC", offset="+00:00", name="UTC"),
        TimezoneInfo(timezone="Europe/Moscow", offset="+03:00", name="Москва"),
        TimezoneInfo(timezone="Asia/Almaty", offset="+06:00", name="Алматы"),
        TimezoneInfo(timezone="Asia/Astana", offset="+06:00", name="Астана"),
        TimezoneInfo(timezone="Europe/London", offset="+00:00", name="Лондон"),
        TimezoneInfo(timezone="Europe/Berlin", offset="+01:00", name="Берлин"),
        TimezoneInfo(timezone="America/New_York", offset="-05:00", name="Нью-Йорк"),
        TimezoneInfo(timezone="Asia/Tokyo", offset="+09:00", name="Токио"),
    ]
    
    return timezones


@router.get(
    "/health",
    summary="Проверка работоспособности модуля доступности",
    description="Endpoint для проверки работоспособности модуля доступности",
    responses={
        200: {"description": "Модуль работает корректно"},
    }
)
async def availability_health_check() -> Dict[str, Any]:
    """Проверка работоспособности модуля доступности."""
    return {
        "status": "healthy",
        "module": "availability",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "availability_rules",
            "time_off_management", 
            "slot_generation",
            "calendar_generation",
            "conflict_detection",
            "bulk_operations",
            "timezone_support"
        ]
    }

