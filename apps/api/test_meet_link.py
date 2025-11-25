"""
Тест проверки работоспособности Google Meet ссылки.
"""
import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrations.google_calendar import _generate_meet_code
from datetime import datetime, timezone, timedelta
from uuid import uuid4

async def test_meet_link():
    print("=" * 60)
    print("ТЕСТ GOOGLE MEET ССЫЛКИ")
    print("=" * 60)
    print()
    
    booking_id = uuid4()
    starts_at = datetime.now(timezone.utc) + timedelta(days=1)
    
    print("1. Генерация ссылки:")
    meet_code = _generate_meet_code(booking_id, starts_at)
    meet_url = f"https://meet.google.com/{meet_code}"
    print(f"   booking_id: {booking_id}")
    print(f"   starts_at: {starts_at.isoformat()}")
    print(f"   meet_code: {meet_code}")
    print(f"   meet_url: {meet_url}")
    print()
    
    print("2. Проверка формата:")
    print(f"   Формат правильный: {meet_url.startswith('https://meet.google.com/')}")
    print(f"   Код имеет формат xxx-yyyy-zzz: {len(meet_code.split('-')) == 3}")
    print()
    
    print("3. ВАЖНО:")
    print("   ⚠️  Сгенерированная ссылка может НЕ работать, потому что")
    print("      это не настоящая встреча, созданная через Google Calendar API.")
    print()
    print("   ✅ Для создания РАБОЧЕЙ Google Meet ссылки нужен:")
    print("      - Google Workspace аккаунт")
    print("      - Или Domain-Wide Delegation для Service Account")
    print()
    print("   💡 Альтернатива: Jitsi Meet (бесплатно, без API ключей)")
    print("      - Можно создавать ссылки программно")
    print("      - Работает без ограничений")
    print()
    
    print("=" * 60)
    print("РЕКОМЕНДАЦИЯ:")
    print("=" * 60)
    print("Для production используйте:")
    print("1. Google Workspace + Domain-Wide Delegation (для Google Meet)")
    print("2. Или Jitsi Meet (бесплатно, без ограничений)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_meet_link())

