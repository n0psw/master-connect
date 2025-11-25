#!/usr/bin/env python3
"""
Прямой тест логина без запуска сервера.
"""
import sys
import asyncio
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.security import verify_password
from modules.users.domain.models import User

# Импортируем все модели для правильной инициализации SQLAlchemy
from modules.users.domain.models import Student
from modules.mentors.domain.models import Mentor, MentorUniversity
from modules.auth.domain.models import RefreshToken
from modules.availability.domain.models import AvailabilityRule, TimeOff
from modules.bookings.domain.models import Booking
from modules.reviews.domain.models import Review
from modules.chat.domain.models import Dialog, Message
from modules.support.domain.models import SupportTicket
from modules.payments.domain.models import PaymentEvidence
from modules.settings.domain.models import GlobalSettings
from modules.admin.domain.models import AuditLog

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_login_direct():
    """Прямой тест логина."""
    
    # Подключаемся к базе данных
    database_url = "sqlite+aiosqlite:///test.db"
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("=== Прямой тест логина ===")
    
    async with async_session() as session:
        # Тестируем логин для всех тестовых аккаунтов
        test_accounts = [
            ("admin@test.com", "password123"),
            ("mentor@test.com", "password123"),
            ("student@test.com", "password123")
        ]
        
        for email, password in test_accounts:
            print(f"\nТестируем: {email}")
            
            # Ищем пользователя
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"  [ERROR] User not found")
                continue
            
            print(f"  [OK] User found: {user.name}")
            print(f"  Role: {user.role}")
            print(f"  Active: {user.is_active}")
            
            # Проверяем пароль
            password_valid = verify_password(password, user.password_hash)
            print(f"  Password valid: {password_valid}")
            
            if password_valid:
                print(f"  [SUCCESS] LOGIN SHOULD WORK!")
            else:
                print(f"  [ERROR] Wrong password")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_login_direct())
