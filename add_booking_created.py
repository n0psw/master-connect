import os
import sys
from pathlib import Path

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / 'apps' / 'api' / 'src'))

from core.config import settings
import psycopg

# Получаем DATABASE_URL и конвертируем в синхронный формат
db_url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

print("Adding BOOKING_CREATED to notification_type ENUM...")

try:
    with psycopg.connect(db_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_CREATED';")
            print("✓ BOOKING_CREATED added successfully!")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

