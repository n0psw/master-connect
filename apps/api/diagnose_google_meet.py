"""
Диагностика Google Meet интеграции.
"""
import sys
import os
sys.path.insert(0, 'src')
sys.stdout.reconfigure(encoding='utf-8')

from core.config import settings
from integrations.google_calendar import google_calendar_service

print("=" * 80)
print("GOOGLE MEET DIAGNOSTICS")
print("=" * 80)

print(f"\n[CONFIG]")
print(f"  GOOGLE_CALENDAR_ENABLED: {settings.GOOGLE_CALENDAR_ENABLED}")
print(f"  GOOGLE_SERVICE_ACCOUNT_FILE: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
print(f"  GOOGLE_SERVICE_ACCOUNT_JSON_B64: {'SET' if settings.GOOGLE_SERVICE_ACCOUNT_JSON_B64 else 'NOT SET'}")
print(f"  GOOGLE_CALENDAR_ID: {settings.GOOGLE_CALENDAR_ID}")
print(f"  GOOGLE_CALENDAR_DELEGATED_USER: {getattr(settings, 'GOOGLE_CALENDAR_DELEGATED_USER', 'NOT SET')}")

print(f"\n[SERVICE STATUS]")
print(f"  Service available: {google_calendar_service.is_available()}")
print(f"  Service object exists: {google_calendar_service.service is not None}")

if settings.GOOGLE_SERVICE_ACCOUNT_FILE:
    file_exists = os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE)
    print(f"  Service Account file exists: {file_exists}")
    if file_exists:
        print(f"  File path: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
    else:
        print(f"  ERROR: File not found at: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")

print(f"\n[RECOMMENDATIONS]")
if not settings.GOOGLE_CALENDAR_ENABLED:
    print("  ❌ GOOGLE_CALENDAR_ENABLED is False - enable it in .env")
if not google_calendar_service.is_available():
    print("  ❌ Service is not available - check credentials")
    if not settings.GOOGLE_SERVICE_ACCOUNT_FILE and not settings.GOOGLE_SERVICE_ACCOUNT_JSON_B64:
        print("     → Set GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_JSON_B64")
    if not settings.GOOGLE_CALENDAR_ID:
        print("     → Set GOOGLE_CALENDAR_ID (your email or 'primary')")
else:
    print("  ✅ Service is available and ready to create meetings")

print("\n" + "=" * 80)

