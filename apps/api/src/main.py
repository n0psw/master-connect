"""
Главный файл FastAPI приложения MasterConnect.
"""
import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError

from core.config import settings
from core.exceptions import (
    MasterConnectException,
    generic_exception_handler,
    http_exception_handler,
    masterconnect_exception_handler,
    validation_exception_handler,
)
from core.logging import get_logger, setup_logging
from core.middleware import setup_middleware
from sqlalchemy.orm import configure_mappers
from db.session import engine
from db.base import Base
from db.session import close_db, init_db

# Импорт роутеров
from modules.auth.api.routes import router as auth_router
from modules.users.api.routes import router as users_router
from modules.mentors.api.routes import router as mentors_router
from modules.availability.api.routes import router as availability_router
from modules.bookings.api.routes import router as bookings_router
from modules.admin.api.routes import router as admin_router
from modules.payments.api.routes import router as payments_router
from modules.chat.api.routes import router as chat_router
from modules.reviews.api.routes import router as reviews_router
from modules.notifications.api.routes import router as notifications_router
from modules.support.api.routes import router as support_router
from modules.health.api.routes import router as health_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения."""
    import asyncio
    from db.session import get_session
    from modules.bookings.application.services import BookingService
    
    # Запуск
    logger.info("Starting MasterConnect API...")
    
    try:
        # Инициализация базы данных
        await init_db()
        logger.info("Database initialized successfully")
        
        # Запускаем фоновую задачу для истечения HOLD бронирований
        async def expire_hold_bookings_task():
            """Периодическая проверка истечения HOLD бронирований."""
            while True:
                try:
                    await asyncio.sleep(60)  # Проверяем каждую минуту
                    db_session = None
                    try:
                        async for session in get_session():
                            db_session = session
                            try:
                                booking_service = BookingService(db_session)
                                expired_count = await booking_service.expire_hold_bookings()
                                if expired_count > 0:
                                    logger.info(f"Expired {expired_count} HOLD bookings")
                            except Exception as e:
                                logger.error(f"Error expiring HOLD bookings: {e}", exc_info=True)
                            break
                    except Exception as e:
                        logger.error(f"Error getting database session: {e}", exc_info=True)
                    finally:
                        if db_session:
                            try:
                                await db_session.close()
                            except Exception:
                                pass
                except asyncio.CancelledError:
                    logger.info("Expire hold bookings task cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in expire_hold_bookings_task: {e}", exc_info=True)
                    await asyncio.sleep(60)  # Ждем перед следующей попыткой
        
        # Запускаем задачу в фоне
        expire_task = asyncio.create_task(expire_hold_bookings_task())
        logger.info("Background task for expiring HOLD bookings started")
        
        # Здесь можно добавить другие инициализации
        # - Redis подключение
        # - Celery
        # - Внешние сервисы
        
        yield
        
    finally:
        # Завершение
        logger.info("Shutting down MasterConnect API...")
        if 'expire_task' in locals():
            expire_task.cancel()
            try:
                await expire_task
            except asyncio.CancelledError:
                pass
        await close_db()
        logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения."""
    
    # Настройка логирования
    setup_logging()
    
    # Создание приложения
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API для платформы MasterConnect - онлайн консультации с менторами",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Настройка middleware
    setup_middleware(app)
    
    # Добавляем TrustedHost middleware для безопасности
    if settings.APP_ENV == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.masterconnect.kz", "masterconnect.kz"]
        )
    
    # В debug режиме включаем подробные ошибки
    if settings.DEBUG:
        # FastAPI автоматически показывает подробные ошибки в debug режиме
        pass
    
    # Ранняя валидация мапперов и (dev) создание таблиц
    try:
        # Явный аггрегирующий импорт всех моделей (важно для регистрации relationship)
        import db.models  # noqa: F401
        # Попытка сконфигурировать мапперы
        configure_mappers()
    except Exception as e:
        logger.error("Mapper configuration failed", error=str(e))
        raise

    # Регистрация обработчиков исключений
    app.add_exception_handler(MasterConnectException, masterconnect_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Подключение роутеров
    app.include_router(auth_router, prefix=settings.API_PREFIX)
    app.include_router(users_router, prefix=settings.API_PREFIX)
    app.include_router(mentors_router, prefix=settings.API_PREFIX)
    app.include_router(availability_router, prefix=settings.API_PREFIX)
    app.include_router(bookings_router, prefix=settings.API_PREFIX)
    app.include_router(admin_router, prefix=settings.API_PREFIX)
    app.include_router(payments_router, prefix=settings.API_PREFIX)
    app.include_router(chat_router, prefix=settings.API_PREFIX)
    app.include_router(reviews_router, prefix=settings.API_PREFIX)
    app.include_router(notifications_router, prefix=settings.API_PREFIX)
    app.include_router(support_router, prefix=settings.API_PREFIX)
    app.include_router(health_router, prefix=settings.API_PREFIX)
    
    # Настройка статических файлов для загрузок
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Проверка состояния приложения."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Корневой endpoint."""
        return {
            "message": "Welcome to MasterConnect API",
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else "Documentation available for authenticated users"
        }
    
    logger.info(
        "FastAPI application created",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        debug=settings.DEBUG
    )
    
    return app


# Создаем экземпляр приложения
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None,  # Используем наш собственный логгер
    )
