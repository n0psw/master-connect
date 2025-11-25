#!/usr/bin/env python3
"""
Скрипт для создания администратора в системе MasterConnect.
"""
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулям приложения
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api" / "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from modules.users.domain.models import User, UserRole
from modules.auth.domain.schemas import RegisterRequest
from modules.auth.application.services import AuthService
from passlib.context import CryptContext

# Настройки хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)

async def create_admin_user():
    """Создание администратора."""
    print("🔧 Создание администратора MasterConnect...")
    
    # Получаем данные от пользователя
    print("\nВведите данные администратора:")
    email = input("Email: ").strip()
    if not email:
        print("❌ Email не может быть пустым!")
        return
    
    password = input("Пароль (минимум 8 символов, буквы + цифры): ").strip()
    if not password:
        print("❌ Пароль не может быть пустым!")
        return
    
    if len(password) < 8:
        print("❌ Пароль должен содержать минимум 8 символов!")
        return
    
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        print("❌ Пароль должен содержать как минимум одну букву и одну цифру!")
        return
    
    name = input("Имя: ").strip()
    if not name:
        print("❌ Имя не может быть пустым!")
        return
    
    phone = input("Телефон (опционально): ").strip() or None
    
    # Создаем пользователя-администратора
    admin_user = User(
        email=email,
        password_hash=get_password_hash(password),
        name=name,
        role=UserRole.ADMIN,
        phone=phone,
        timezone="UTC",
        locale="ru",
        is_active=True
    )
    
    # Сохраняем в базу данных
    async for session in get_session():
        try:
            # Проверяем, не существует ли уже пользователь с таким email
            from sqlalchemy import text
            existing_user = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            if existing_user.fetchone():
                print(f"❌ Пользователь с email {email} уже существует!")
                return
            
            session.add(admin_user)
            await session.commit()
            
            print(f"\n✅ Администратор успешно создан!")
            print(f"📧 Email: {email}")
            print(f"👤 Имя: {name}")
            print(f"🔑 Роль: {UserRole.ADMIN}")
            print(f"\n🌐 Теперь вы можете войти в систему:")
            print(f"   - API: http://localhost:8000/docs")
            print(f"   - Логин: POST /api/v1/auth/login")
            
        except Exception as e:
            print(f"❌ Ошибка при создании администратора: {e}")
            await session.rollback()
        finally:
            await session.close()
        break

if __name__ == "__main__":
    asyncio.run(create_admin_user())
