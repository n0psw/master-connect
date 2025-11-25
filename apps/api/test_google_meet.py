"""
Тестовый скрипт для проверки создания Google Meet ссылок.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations.google_calendar import google_calendar_service
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


async def test_google_meet_creation():
    """Тест создания Google Meet ссылки."""
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ GOOGLE MEET ССЫЛКИ")
    print("=" * 60)
    print()
    
    # Проверка настроек
    print("1. Проверка настроек:")
    print(f"   GOOGLE_CALENDAR_ENABLED: {settings.GOOGLE_CALENDAR_ENABLED}")
    print(f"   GOOGLE_SERVICE_ACCOUNT_FILE: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
    print(f"   GOOGLE_CALENDAR_ID: {settings.GOOGLE_CALENDAR_ID}")
    print()
    
    # Проверка доступности сервиса
    print("2. Проверка доступности Google Calendar сервиса:")
    is_available = google_calendar_service.is_available()
    print(f"   is_available(): {is_available}")
    print(f"   service is None: {google_calendar_service.service is None}")
    print()
    
    if not is_available:
        print("[ERROR] Google Calendar сервис недоступен!")
        print()
        print("Возможные причины:")
        print("  - GOOGLE_CALENDAR_ENABLED=False")
        print("  - Service Account файл не найден")
        print("  - Service Account не инициализирован")
        print("  - Service Account не имеет доступа к календарю")
        print()
        return False
    
    print("[OK] Google Calendar сервис доступен!")
    print()
    
    # Тестовые данные
    booking_id = uuid4()
    student_name = "Тестовый Студент"
    student_email = "student@test.com"
    mentor_name = "Тестовый Ментор"
    mentor_email = "mentor@test.com"
    starts_at = datetime.now(timezone.utc) + timedelta(days=1)
    duration_minutes = 30
    
    print("3. Тестовые данные:")
    print(f"   booking_id: {booking_id}")
    print(f"   student: {student_name} ({student_email})")
    print(f"   mentor: {mentor_name} ({mentor_email})")
    print(f"   starts_at: {starts_at.isoformat()}")
    print(f"   duration: {duration_minutes} минут")
    print()
    
    # Попытка создания встречи
    print("4. Создание Google Meet встречи...")
    try:
        result = await google_calendar_service.create_meeting(
            booking_id=booking_id,
            student_name=student_name,
            student_email=student_email,
            mentor_name=mentor_name,
            mentor_email=mentor_email,
            starts_at=starts_at,
            duration_minutes=duration_minutes
        )
        
        print("[OK] Встреча создана успешно!")
        print()
        print("5. Результат:")
        print(f"   event_id: {result.get('event_id')}")
        print(f"   meeting_url: {result.get('meeting_url')}")
        print(f"   html_link: {result.get('html_link')}")
        print()
        
        # Проверка типа ссылки
        meeting_url = result.get('meeting_url', '')
        if meeting_url.startswith('https://meet.google.com/dev-'):
            print("[WARNING] ВНИМАНИЕ: Создана dev-ссылка (тестовая)!")
            print()
            print("Это означает, что:")
            print("  - Google Calendar API не может создать реальное событие")
            print("  - Service Account не имеет доступа к календарю")
            print("  - Или есть ошибка при создании события")
            print()
            print("Решение:")
            print("  1. Откройте Google Calendar: https://calendar.google.com/")
            print("  2. Настройки -> Общий доступ")
            print(f"  3. Добавьте: masterconnect-calendar@masterconnect-478812.iam.gserviceaccount.com")
            print("  4. Права: 'Изменение мероприятий'")
            print("  5. Сохраните и перезапустите backend")
            return False
        elif meeting_url.startswith('https://meet.google.com/'):
            print("[OK] Создана РЕАЛЬНАЯ Google Meet ссылка!")
            print()
            print("Ссылка работает и готова к использованию!")
            return True
        else:
            print(f"[WARNING] Неожиданный формат ссылки: {meeting_url}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при создании встречи: {e}")
        print()
        print("Детали ошибки:")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    result = asyncio.run(test_google_meet_creation())
    print("=" * 60)
    if result:
        print("[OK] ТЕСТ ПРОЙДЕН")
    else:
        print("[ERROR] ТЕСТ НЕ ПРОЙДЕН")
    print("=" * 60)
    print()

