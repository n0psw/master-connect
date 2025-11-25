#!/usr/bin/env python3
"""
Скрипт для создания демо-пользователей в базе данных MasterConnect.

Создает следующих пользователей:
- admin@test.com (пароль: password123) - Администратор
- mentor@test.com (пароль: password123) - Ментор
- student@test.com (пароль: password123) - Студент

Использование:
    python create_demo_users.py
"""
import asyncio
import sys
from pathlib import Path

# Добавляем src в path чтобы импорты работали
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.security import get_password_hash
from modules.users.domain.models import User, UserRole, Student
from modules.mentors.domain.models import Mentor
from db.base import Base


# Конфигурация демо пользователей
DEMO_USERS = [
    {
        "email": "admin@test.com",
        "password": "password123", 
        "role": UserRole.ADMIN,
        "name": "Администратор Системы",
        "timezone": "Asia/Almaty",
        "locale": "ru"
    },
    {
        "email": "mentor@test.com",
        "password": "password123",
        "role": UserRole.MENTOR, 
        "name": "Айдар Нурланов",
        "timezone": "Asia/Almaty",
        "locale": "ru"
    },
    {
        "email": "student@test.com", 
        "password": "password123",
        "role": UserRole.STUDENT,
        "name": "Амир Каримов", 
        "timezone": "Asia/Almaty",
        "locale": "ru"
    }
]


async def create_demo_users():
    """Создание демо-пользователей."""
    
    # Используем SQLite базу данных для демо-пользователей
    database_url = "sqlite+aiosqlite:///test.db"
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        # Создаем таблицы если их нет
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Таблицы созданы/обновлены")
        
        # Создаем пользователей
        async with async_session() as session:
            created_users = []
            
            for user_data in DEMO_USERS:
                # Проверяем, существует ли пользователь
                result = await session.execute(
                    select(User).where(User.email == user_data["email"])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"⚠️  Пользователь {user_data['email']} уже существует, пропускаем")
                    continue
                
                # Создаем нового пользователя
                password_hash = get_password_hash(user_data["password"])
                
                user = User(
                    email=user_data["email"],
                    password_hash=password_hash,
                    role=user_data["role"],
                    name=user_data["name"],
                    timezone=user_data["timezone"],
                    locale=user_data["locale"],
                    is_active=True
                )
                
                session.add(user)
                await session.flush()  # Получаем ID пользователя
                
                # Создаем профили для специальных ролей
                if user.role == UserRole.STUDENT:
                    student_profile = Student(
                        user_id=user.id,
                        goals="Хочу поступить в топовый университет за границей. Интересует Computer Science и данная отрасль.",
                        country="Казахстан",
                        city="Алматы"
                    )
                    session.add(student_profile)
                
                elif user.role == UserRole.MENTOR:
                    mentor_profile = Mentor(
                        user_id=user.id,
                        headline="Senior Software Engineer в Google, выпускник MIT",
                        bio="Имею 8+ лет опыта в разработке ПО, работал в Google, Facebook. Выпускник MIT по Computer Science. Помогаю студентам поступать в топовые университеты и развиваться в IT.",
                        price_30=50,
                        price_45=70,
                        price_60=90,
                        languages=["Русский", "Английский", "Казахский"],
                        subjects=["Computer Science", "Software Engineering", "Admissions"]
                    )
                    session.add(mentor_profile)
                    
                    # Добавляем университет ментора
                    mentor_university = MentorUniversity(
                        mentor_id=user.id,
                        university="Massachusetts Institute of Technology (MIT)",
                        degree="Bachelor of Science",
                        major="Computer Science",
                        year_from=2010,
                        year_to=2014,
                        country="США",
                        city="Кембридж"
                    )
                    session.add(mentor_university)
                
                created_users.append(user)
                print(f"✅ Создан пользователь: {user.email} ({user.role}) - {user.name}")
            
            # Сохраняем изменения
            if created_users:
                await session.commit()
                print(f"\n🎉 Успешно создано {len(created_users)} пользователей!")
            else:
                print("\n⚠️  Все демо-пользователи уже существуют")
            
            # Выводим итоговую информацию
            print("\n" + "="*50)
            print("ДЕМО АККАУНТЫ:")
            print("="*50)
            for user_data in DEMO_USERS:
                print(f"📧 {user_data['email']}")
                print(f"🔒 Пароль: {user_data['password']}")
                print(f"👤 Роль: {user_data['role']}")
                print(f"📛 Имя: {user_data['name']}")
                print("-" * 30)
            
            print("\n🌐 Перейдите на http://localhost:5173 для входа в систему")
            print("📚 API документация: http://localhost:8000/docs")
                
    except Exception as e:
        print(f"❌ Ошибка при создании пользователей: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("🚀 Создание демо-пользователей MasterConnect...")
    print("-" * 50)
    
    # Запускаем асинхронную функцию
    asyncio.run(create_demo_users())
