from datetime import datetime, timedelta, timezone
from typing import Iterable

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from modules.bookings.domain.models import Booking, BookingStatus
from modules.notifications.application.services import create_notification_helper
from modules.notifications.domain.models import Notification, NotificationType
from modules.users.domain.models import User


def _normalize_dt(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


async def _get_user_timezone(db: AsyncSession, user_id) -> str:
    stmt = select(User.timezone).where(User.id == user_id)
    result = await db.execute(stmt)
    tz = result.scalar_one_or_none()
    return tz or "Etc/GMT-5"


def _format_datetime_in_tz(dt: datetime, tz_str: str) -> str:
    dt_utc = _normalize_dt(dt)
    try:
        tz = pytz.timezone(tz_str)
        dt_local = dt_utc.astimezone(tz)
        return dt_local.strftime("%d.%m %H:%M")
    except Exception:
        return dt_utc.astimezone(timezone.utc).strftime("%d.%m %H:%M")


async def _has_reminder(db: AsyncSession, booking_id, title: str) -> bool:
    stmt = (
        select(Notification.id)
        .where(
            and_(
                Notification.type == NotificationType.BOOKING_REMINDER,
                Notification.related_entity_id == booking_id,
                Notification.title == title,
            )
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def _send_reminder(db: AsyncSession, booking: Booking, minutes: int, title: str) -> None:
    student_tz = await _get_user_timezone(db, booking.student_id)
    mentor_tz = await _get_user_timezone(db, booking.mentor_id)
    
    start_str_student = _format_datetime_in_tz(booking.starts_at, student_tz)
    start_str_mentor = _format_datetime_in_tz(booking.starts_at, mentor_tz)
    
    message_student = f"Консультация начнется {start_str_student}. Осталось {minutes} минут."
    message_mentor = f"Сессия со студентом начнется {start_str_mentor}. Осталось {minutes} минут."
    await create_notification_helper(
        db=db,
        user_id=booking.student_id,
        notification_type=NotificationType.BOOKING_REMINDER,
        title=title,
        message=message_student,
        related_entity_type="booking",
        related_entity_id=booking.id,
        action_url=f"/student/bookings/{booking.id}",
    )
    await create_notification_helper(
        db=db,
        user_id=booking.mentor_id,
        notification_type=NotificationType.BOOKING_REMINDER,
        title=title,
        message=message_mentor,
        related_entity_type="booking",
        related_entity_id=booking.id,
        action_url=f"/mentor/bookings/{booking.id}",
    )


async def process_booking_reminders(
    db: AsyncSession,
    now_utc: datetime,
    targets: Iterable[tuple[int, str]],
) -> int:
    created = 0
    for minutes, title_suffix in targets:
        window_start = now_utc + timedelta(minutes=minutes)
        window_end = now_utc + timedelta(minutes=minutes + 5)
        stmt = select(Booking).where(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.starts_at >= window_start,
                Booking.starts_at < window_end,
            )
        )
        result = await db.execute(stmt)
        bookings = result.scalars().all()
        title = f"Напоминание о консультации ({title_suffix})"
        for booking in bookings:
            if await _has_reminder(db, booking.id, title):
                continue
            await _send_reminder(db, booking, minutes, title)
            created += 1
    return created

