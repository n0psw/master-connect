#!/usr/bin/env python3
"""
Dev-seed для локальной SQLite: создает 1 admin, 2 mentors (с доступностями), 3 students и 3 брони.
Использует только AsyncSession (никакого raw sqlite3).
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, time
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

sys.path.insert(0, str(Path(__file__).parent / "src"))

# Импорт моделей и сессии после добавления src в sys.path
import db.models  # noqa: F401 - агрегирующий импорт всех моделей
from db.session import SessionLocal, engine
from db.base import Base
from core.logging import get_logger

from modules.users.domain.models import User, UserRole, Student
from modules.mentors.domain.models import Mentor
from modules.availability.domain.models import AvailabilityRule
from modules.bookings.domain.models import Booking, BookingStatus


logger = get_logger(__name__)


async def ensure_user(session, email: str, role: UserRole, name: str) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        return user

    from core.security import get_password_hash
    user = User(
        id=uuid4(),
        email=email.lower(),
        password_hash=get_password_hash("password123"),
        role=role,
        name=name,
        timezone="Asia/Almaty",
        locale="ru",
        is_active=True,
    )
    session.add(user)
    await session.flush()

    # Профили для STUDENT/MENTOR
    if role == UserRole.STUDENT:
        session.add(Student(user_id=user.id, goals="Готовлюсь к поступлению", country="Казахстан", city="Алматы"))
    if role == UserRole.MENTOR:
        session.add(Mentor(user_id=user.id, headline="Senior Engineer", bio="Помогаю студентам"))

    return user


async def ensure_availability(session, mentor_user_id, weekday: int, start: time, end: time) -> None:
    # Простое правило доступности для ментора
    rule = AvailabilityRule(
        id=uuid4(),
        mentor_id=mentor_user_id,
        weekday=weekday,
        time_start=start,
        time_end=end,
        slot_duration_minutes=60,
        buffer_minutes=10,
        breaks_json=[],
    )
    session.add(rule)


async def create_booking(
    session,
    student_user_id,
    mentor_user_id,
    starts_at: datetime,
    minutes: int = 60,
) -> Booking:
    booking = Booking(
        id=uuid4(),
        student_id=student_user_id,
        mentor_id=mentor_user_id,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(minutes=minutes),
        duration_minutes=minutes,
        price=Decimal("100.00"),
        currency="KZT",
        status=BookingStatus.AWAITING_VERIFICATION,
        intake_form={},
        payment_status="UNPAID",
    )
    session.add(booking)
    return booking


async def main():
    # Убедимся, что мапперы сконфигурированы до начала работы
    configure_mappers()
    # Dev: пересоздадим схему, чтобы гарантировать наличие всех колонок
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        # Users
        admin = await ensure_user(session, "admin@test.com", UserRole.ADMIN, "Администратор")
        mentor1 = await ensure_user(session, "mentor1@test.com", UserRole.MENTOR, "Ментор 1")
        mentor2 = await ensure_user(session, "mentor2@test.com", UserRole.MENTOR, "Ментор 2")
        student1 = await ensure_user(session, "student1@test.com", UserRole.STUDENT, "Студент 1")
        student2 = await ensure_user(session, "student2@test.com", UserRole.STUDENT, "Студент 2")
        student3 = await ensure_user(session, "student3@test.com", UserRole.STUDENT, "Студент 3")

        # Availability (сегодняшний будний день условно: понедельник=0)
        await ensure_availability(session, mentor1.id, weekday=datetime.utcnow().weekday(), start=time(10, 0), end=time(12, 0))
        await ensure_availability(session, mentor2.id, weekday=datetime.utcnow().weekday(), start=time(14, 0), end=time(16, 0))

        # Bookings: завтра
        base = (datetime.utcnow() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        b1 = await create_booking(session, student1.id, mentor1.id, base)
        b2 = await create_booking(session, student2.id, mentor1.id, base + timedelta(hours=1))
        b3 = await create_booking(session, student3.id, mentor2.id, base.replace(hour=14))

        # Для одной брони — подтверждение оплаты и Zoom
        b1.status = BookingStatus.CONFIRMED
        b1.payment_status = "VERIFIED"
        b1.zoom_join_url = "https://zoom.example/join/" + str(uuid4())
        b1.zoom_start_url = "https://zoom.example/start/" + str(uuid4())

        await session.commit()
        logger.info("Seed completed: users=%s, mentors=%s, students=%s, bookings=3", 1 + 2 + 3, 2, 3)


if __name__ == "__main__":
    asyncio.run(main())


