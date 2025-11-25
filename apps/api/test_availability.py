#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности страницы доступности ментора.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings
from modules.availability.application.services import AvailabilityService
from modules.availability.domain.models import MentorSettings
from modules.mentors.domain.models import Mentor
from modules.users.domain.models import User, UserRole

async def test_availability_functionality():
    """Тестирование функциональности доступности ментора."""
    print("🧪 Тестирование функциональности доступности ментора...")
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        availability_service = AvailabilityService(db)
        
        # 1. Тест получения профиля доступности
        print("\n1️⃣ Тестирование получения профиля доступности...")
        
        # Найдем первого ментора в БД
        from sqlalchemy import select
        mentor_query = select(Mentor).join(User).where(User.role == UserRole.MENTOR).limit(1)
        mentor_result = await db.execute(mentor_query)
        mentor = mentor_result.scalar_one_or_none()
        
        if not mentor:
            print("❌ Менторы не найдены в БД. Создайте демо-пользователей.")
            return False
        
        print(f"✅ Найден ментор: {mentor.user.email}")
        
        try:
            profile = await availability_service.get_mentor_availability_profile(mentor.user_id)
            print(f"✅ Профиль получен: mentor_id={profile.mentor_id}")
            print(f"   - Настройки: timezone={profile.settings.timezone}")
            print(f"   - Расписание: {len(profile.weekly_schedule.monday)} слотов в понедельник")
            print(f"   - Периоды отсутствия: {len(profile.time_offs)}")
        except Exception as e:
            print(f"❌ Ошибка получения профиля: {e}")
            return False
        
        # 2. Тест обновления настроек
        print("\n2️⃣ Тестирование обновления настроек...")
        
        from modules.availability.domain.schemas import MentorSettingsUpdate
        
        settings_update = MentorSettingsUpdate(
            timezone="Asia/Almaty",
            buffer_time_minutes=20,
            max_bookings_per_day=10,
            advance_booking_days=45
        )
        
        try:
            updated_settings = await availability_service.update_mentor_settings(
                mentor.user_id, settings_update
            )
            print(f"✅ Настройки обновлены:")
            print(f"   - timezone: {updated_settings.timezone}")
            print(f"   - buffer_time_minutes: {updated_settings.buffer_time_minutes}")
            print(f"   - max_bookings_per_day: {updated_settings.max_bookings_per_day}")
            print(f"   - advance_booking_days: {updated_settings.advance_booking_days}")
        except Exception as e:
            print(f"❌ Ошибка обновления настроек: {e}")
            return False
        
        # 3. Тест обновления расписания
        print("\n3️⃣ Тестирование обновления расписания...")
        
        from modules.availability.domain.schemas import WeeklyScheduleUpdate, TimeSlot
        
        schedule_update = WeeklyScheduleUpdate(
            monday=[TimeSlot(start_time="09:00", end_time="17:00")],
            tuesday=[TimeSlot(start_time="09:00", end_time="17:00")],
            wednesday=[TimeSlot(start_time="09:00", end_time="17:00")],
            thursday=[TimeSlot(start_time="09:00", end_time="17:00")],
            friday=[TimeSlot(start_time="09:00", end_time="17:00")],
            saturday=[],
            sunday=[]
        )
        
        try:
            updated_schedule = await availability_service.update_weekly_schedule(
                mentor.user_id, schedule_update
            )
            print(f"✅ Расписание обновлено:")
            print(f"   - Понедельник: {len(updated_schedule.monday)} слотов")
            print(f"   - Вторник: {len(updated_schedule.tuesday)} слотов")
            print(f"   - Суббота: {len(updated_schedule.saturday)} слотов")
        except Exception as e:
            print(f"❌ Ошибка обновления расписания: {e}")
            return False
        
        # 4. Тест генерации календаря
        print("\n4️⃣ Тестирование генерации календаря...")
        
        from datetime import date
        
        try:
            calendar = await availability_service.generate_availability_calendar(
                mentor_id=mentor.user_id,
                date_from=date.today() + timedelta(days=1),
                date_to=date.today() + timedelta(days=7),
                duration_minutes=60,
                timezone_str="Asia/Almaty"
            )
            print(f"✅ Календарь сгенерирован:")
            print(f"   - Ментор: {calendar.mentor_id}")
            print(f"   - Период: {calendar.date_from} - {calendar.date_to}")
            print(f"   - Слотов: {len(calendar.slots)}")
            print(f"   - Часовой пояс: {calendar.timezone}")
        except Exception as e:
            print(f"❌ Ошибка генерации календаря: {e}")
            return False
        
        print("\n🎉 Все тесты прошли успешно!")
        return True

async def main():
    """Главная функция."""
    try:
        success = await test_availability_functionality()
        if success:
            print("\n✅ Функциональность доступности ментора работает корректно!")
            print("\n📋 Что было протестировано:")
            print("   ✓ Получение профиля доступности")
            print("   ✓ Обновление настроек ментора")
            print("   ✓ Обновление недельного расписания")
            print("   ✓ Генерация календаря доступности")
            print("\n🚀 Страница доступности ментора готова к использованию!")
        else:
            print("\n❌ Тесты не прошли. Проверьте ошибки выше.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
