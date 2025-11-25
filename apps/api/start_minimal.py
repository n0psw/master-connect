#!/usr/bin/env python3
"""
Минимальный запуск backend сервера.
"""
import sys
import os
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Минимальные переменные окружения
os.environ.update({
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

if __name__ == "__main__":
    import uvicorn
    
    print("Starting backend server...")
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Test accounts:")
    print("  - admin@test.com / password123")
    print("  - mentor@test.com / password123") 
    print("  - student@test.com / password123")
    print()
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info"
    )
