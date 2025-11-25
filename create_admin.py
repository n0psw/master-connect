#!/usr/bin/env python3
"""
Скрипт для создания администратора в MasterConnect.
Использование: python create_admin.py <email> <password> <name>

Для Docker:
docker compose exec api python /app/create_admin.py <email> <password> <name>
"""
import asyncio
import sys
import os
from pathlib import Path

# Определяем путь к приложению
if os.path.exists("/app/src"):  # Docker
    app_path = "/app/src"
else:  # Локально
    app_path = str(Path(__file__).parent / "apps" / "api" / "src")

sys.path.insert(0, app_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from modules.users.domain.models import User, UserRole
from core.security import get_password_hash
from core.config import settings


async def create_admin(email: str, password: str, name: str = "Admin"):
    """Создает администратора в базе данных."""
    
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
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ Пользователь с email {email} уже существует!")
            if existing_user.role == UserRole.ADMIN:
                print("   Это уже администратор. Хотите обновить пароль? (y/n): ", end="")
                response = input().strip().lower()
                if response == 'y':
                    existing_user.password_hash = get_password_hash(password)
                    existing_user.name = name
                    await session.commit()
                    print(f"✅ Пароль администратора {email} обновлен!")
                return
            else:
                print(f"   Текущая роль: {existing_user.role}")
                print("   Хотите сделать его администратором? (y/n): ", end="")
                response = input().strip().lower()
                if response == 'y':
                    existing_user.role = UserRole.ADMIN
                    existing_user.password_hash = get_password_hash(password)
                    existing_user.name = name
                    await session.commit()
                    print(f"✅ Пользователь {email} теперь администратор!")
                return
        
        # Создаем нового администратора
        admin = User(
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            name=name,
            is_active=True,
            timezone="UTC",
            locale="ru"
        )
        
        session.add(admin)
        await session.commit()
        
        print(f"✅ Администратор успешно создан!")
        print(f"   Email: {email}")
        print(f"   Имя: {name}")
        print(f"   Роль: {admin.role}")
    
    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python create_admin.py <email> <password> [name]")
        print("Пример: python create_admin.py admin@example.com MySecurePass123 Admin User")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else "Admin"
    
    if len(password) < 8:
        print("❌ Пароль должен содержать минимум 8 символов!")
        sys.exit(1)
    
    print(f"Создание администратора...")
    print(f"Email: {email}")
    print(f"Имя: {name}")
    
    asyncio.run(create_admin(email, password, name))

