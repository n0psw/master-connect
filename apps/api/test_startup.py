#!/usr/bin/env python3
"""
Тест запуска приложения.
"""
import sys
import os
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Минимальные переменные окружения
os.environ.update({
    'DATABASE_URL': 'sqlite+aiosqlite:///test.db',
    'SECRET_KEY': 'your-secret-key-here',
    'JWT_SECRET_KEY': 'your-jwt-secret-key',
    'APP_ENV': 'development',
    'DEBUG': 'true',
    'BACKEND_CORS_ORIGINS': '["http://localhost:3000","http://localhost:5173","http://localhost:8080"]',
    'REDIS_URL': 'redis://localhost:6379/0',
    'S3_BUCKET': 'dummy',
    'S3_ACCESS_KEY': 'dummy',
    'S3_SECRET_KEY': 'dummy',
    'S3_REGION': 'us-east-1',
    'EMAIL_SMTP_HOST': 'smtp.gmail.com',
    'EMAIL_SMTP_USER': 'dummy@example.com',
    'EMAIL_SMTP_PASSWORD': 'dummy',
    'EMAIL_FROM': 'dummy@example.com',
    'GOOGLE_SERVICE_ACCOUNT_JSON_B64': 'dummy',
    'GOOGLE_CALENDAR_ID': 'dummy',
    'KASPI_PAYMENT_URL': 'dummy',
    'RATE_LIMIT_WINDOW': '60',
    'MAX_FILE_SIZE_MB': '10',
    'ALLOWED_FILE_TYPES': 'pdf,jpg,jpeg,png,docx',
    'BOOKING_HOLD_DURATION_MINUTES': '10'
})

def test_imports():
    """Тест импортов."""
    print("Testing imports...")
    
    try:
        print("  - Importing core.config...")
        from core.config import settings
        print(f"  - Settings loaded: {settings.APP_NAME}")
    except Exception as e:
        print(f"  - Error importing core.config: {e}")
        return False
    
    try:
        print("  - Importing main app...")
        from src.main import app
        print(f"  - App imported: {app}")
    except Exception as e:
        print(f"  - Error importing main app: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_database():
    """Тест базы данных."""
    print("Testing database connection...")
    
    try:
        from core.config import settings
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        import asyncio
        async def test_conn():
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar()
        
        result = asyncio.run(test_conn())
        print(f"  - Database connection OK: {result}")
        
        asyncio.run(engine.dispose())
        return True
        
    except Exception as e:
        print(f"  - Database error: {e}")
        return False

if __name__ == "__main__":
    print("=== Backend Startup Test ===")
    
    if test_imports():
        print("[OK] Imports OK")
    else:
        print("[ERROR] Import failed")
        sys.exit(1)
    
    if test_database():
        print("[OK] Database OK")
    else:
        print("[ERROR] Database failed")
        sys.exit(1)
    
    print("[SUCCESS] All tests passed!")
    print("Backend should be able to start.")
