#!/usr/bin/env python3
"""
Скрипт для создания демо-аккаунтов (студент, ментор, админ).
Использование: python create_demo_users.py

Для Docker:
docker compose exec api python /app/create_demo_users.py
"""
import asyncio
import sys
import os
from pathlib import Path
from decimal import Decimal

# Определяем путь к приложению
if os.path.exists("/app/src"):  # Docker
    app_path = "/app/src"
else:  # Локально
    app_path = str(Path(__file__).parent / "apps" / "api" / "src")

sys.path.insert(0, app_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from modules.users.domain.models import User, Student, UserRole
from modules.mentors.domain.models import Mentor
from core.security import get_password_hash
from core.config import settings


async def create_demo_users():
    """Создает демо-аккаунты: студент, ментор и админ."""
    
    # Подключаемся к базе данных
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        demo_password = "password123"
        
        # 1. Создаем демо-студента
        student_email = "student@test.com"
        student_name = "Демо Студент"
        
        result = await session.execute(
            select(User).where(User.email == student_email)
        )
        existing_student = result.scalar_one_or_none()
        
        if existing_student:
            print(f"⚠️  Студент {student_email} уже существует, пропускаем...")
        else:
            student_user = User(
                email=student_email,
                password_hash=get_password_hash(demo_password),
                name=student_name,
                role=UserRole.STUDENT,
                is_active=True,
                timezone="Asia/Almaty",
                locale="ru"
            )
            session.add(student_user)
            await session.flush()
            
            # Создаем профиль студента
            student_profile = Student(user_id=student_user.id)
            session.add(student_profile)
            
            print(f"✅ Студент создан: {student_email}")
        
        # 2. Создаем демо-ментора
        mentor_email = "mentor@test.com"
        mentor_name = "Демо Ментор"
        
        result = await session.execute(
            select(User).where(User.email == mentor_email)
        )
        existing_mentor_user = result.scalar_one_or_none()
        
        if existing_mentor_user:
            print(f"⚠️  Ментор {mentor_email} уже существует, пропускаем...")
        else:
            mentor_user = User(
                email=mentor_email,
                password_hash=get_password_hash(demo_password),
                name=mentor_name,
                role=UserRole.MENTOR,
                is_active=True,
                timezone="Asia/Almaty",
                locale="ru"
            )
            session.add(mentor_user)
            await session.flush()
            
            # Создаем профиль ментора
            mentor_profile = Mentor(
                user_id=mentor_user.id,
                headline="Опытный наставник по поступлению в зарубежные университеты",
                bio="Помогаю студентам поступить в топовые университеты мира. Опыт работы более 5 лет.",
                price_30=Decimal("5000.00"),
                price_45=Decimal("7000.00"),
                price_60=Decimal("9000.00"),
                languages=["Русский", "Английский"],
                subjects=["Поступление в университет", "Подготовка к IELTS", "Написание эссе"],
                rating_avg=Decimal("4.90"),
                rating_count=25
            )
            session.add(mentor_profile)
            
            print(f"✅ Ментор создан: {mentor_email}")
        
        # 3. Создаем демо-админа
        admin_email = "admin@test.com"
        admin_name = "Демо Админ"
        
        result = await session.execute(
            select(User).where(User.email == admin_email)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"⚠️  Админ {admin_email} уже существует, пропускаем...")
        else:
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash(demo_password),
                name=admin_name,
                role=UserRole.ADMIN,
                is_active=True,
                timezone="Asia/Almaty",
                locale="ru"
            )
            session.add(admin_user)
            
            print(f"✅ Админ создан: {admin_email}")
        
        # Коммитим все изменения
        await session.commit()
        
        print("\n" + "="*50)
        print("✅ Все демо-аккаунты созданы!")
        print("="*50)
        print(f"Студент: {student_email} / {demo_password}")
        print(f"Ментор:  {mentor_email} / {demo_password}")
        print(f"Админ:   {admin_email} / {demo_password}")
        print("="*50)
    
    await engine.dispose()


if __name__ == "__main__":
    print("Создание демо-аккаунтов...")
    asyncio.run(create_demo_users())

