"""
Сессия базы данных и dependency injection.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Создаем асинхронный движок базы данных
# Используем стандартный пул соединений для PostgreSQL
# SQLite больше не поддерживается для обеспечения совместимости с production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

# Создаем фабрику сессий
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор сессии базы данных.
    Используется для создания новых сессий в тестах и background задачах.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в FastAPI.
    """
    async for session in get_session():
        yield session


async def init_db() -> None:
    """
    Инициализация базы данных.
    Создает все таблицы, если они не существуют.
    """
    from .base import Base
    
    # Импортируем все модели, чтобы они были зарегистрированы
    # Порядок импортов важен для избежания циклических зависимостей
    try:
        # Базовые модели
        from modules.users.domain.models import User, Student
        from modules.mentors.domain.models import Mentor, MentorUniversity
        from modules.auth.domain.models import RefreshToken
        from modules.support.domain.models import SupportTicket
        from modules.admin.domain.models import AuditLog
        from modules.chat.domain.models import Dialog, Message
        
        # Модели с зависимостями
        from modules.availability.domain.models import AvailabilityRule, TimeOff, MentorSettings
        from modules.bookings.domain.models import Booking
        from modules.reviews.domain.models import Review
        from modules.payments.domain.models import PaymentEvidence
        from modules.settings.domain.models import GlobalSettings
        from modules.notifications.domain.models import Notification
    except ImportError as e:
        logger.warning(f"Failed to import some models: {e}")
        # Импортируем только основные модели
        from modules.users.domain.models import User, Student
        from modules.auth.domain.models import RefreshToken
    
    logger.info("Creating database tables...")
    
    async with engine.begin() as conn:
        # Создаем все таблицы только если они не существуют
        # Миграции Alembic должны управлять схемой БД
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    
    logger.info("Database tables created successfully")


async def close_db() -> None:
    """
    Закрытие подключения к базе данных.
    """
    await engine.dispose()
    logger.info("Database connection closed")
