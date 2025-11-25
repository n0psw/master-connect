#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления ошибки сериализации.
"""
import asyncio
import sys
import os
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

async def test_mentor_settings_serialization():
    """Тестирование сериализации настроек ментора."""
    print("Тестирование сериализации настроек ментора...")
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        availability_service = AvailabilityService(db)
        
        # Найдем первого ментора в БД
        from sqlalchemy import select
        mentor_query = select(Mentor).join(User).where(User.role == UserRole.MENTOR).limit(1)
        mentor_result = await db.execute(mentor_query)
        mentor = mentor_result.scalar_one_or_none()
        
        if not mentor:
            print("Менторы не найдены в БД")
            return False
        
        print(f"Найден ментор: {mentor.user.email}")
        
        try:
            profile = await availability_service.get_mentor_availability_profile(mentor.user_id)
            print(f"Профиль получен успешно: mentor_id={profile.mentor_id}")
            print(f"Настройки: timezone={profile.settings.timezone}")
            print(f"created_at: {profile.settings.created_at} (тип: {type(profile.settings.created_at)})")
            print(f"updated_at: {profile.settings.updated_at} (тип: {type(profile.settings.updated_at)})")
            return True
        except Exception as e:
            print(f"Ошибка получения профиля: {e}")
            return False

async def main():
    """Главная функция."""
    try:
        success = await test_mentor_settings_serialization()
        if success:
            print("\nСериализация работает корректно!")
            print("Ошибка исправлена!")
        else:
            print("\nОшибка все еще есть")
            sys.exit(1)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
