import os
import sys
from pathlib import Path

root = Path(__file__).parent
sys.path.insert(0, str(root / 'apps' / 'api' / 'src'))

from core.config import settings
import psycopg

db_url = settings.DATABASE_URL
if 'postgresql+asyncpg://' in db_url:
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
elif 'postgresql+psycopg://' in db_url:
    db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')

print("Adding BOOKING_CREATED to notification_type ENUM...")
print(f"Database: {db_url.split('@')[-1] if '@' in db_url else 'unknown'}")

try:
    conn = psycopg.connect(db_url, autocommit=True)
    cur = conn.cursor()
    
    cur.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'BOOKING_CREATED';")
    
    cur.close()
    conn.close()
    
    print("✓ SUCCESS! BOOKING_CREATED added to ENUM")
    print("Now you can use NotificationType.BOOKING_CREATED in code")
    
except psycopg.errors.DuplicateObject:
    print("✓ BOOKING_CREATED already exists in ENUM")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

