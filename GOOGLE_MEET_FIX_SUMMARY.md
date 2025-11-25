# Исправления Google Meet интеграции

## Проблемы и решения

### 1. ✅ Обновление статуса без перезагрузки страницы
**Проблема:** После подтверждения бронирования админом, студент не видел обновленный статус без перезагрузки.

**Решение:** Добавлена инвалидация всех связанных запросов в `PaymentEvidenceViewer.tsx`:
- `['admin-bookings']`
- `['moderation-queue']`
- `['my-bookings']` ← **добавлено**
- `['booking-stats']` ← **добавлено**
- `['booking']` ← **добавлено**

### 2. 🔧 Google Meet - Service Account ограничения

**Проблема 1:** `403 Forbidden - Service accounts cannot invite attendees without Domain-Wide Delegation`

**Решение:** Убраны `attendees` из события. Service Account не может приглашать участников без Domain-Wide Delegation (требует Google Workspace).

**Проблема 2:** `400 Invalid conference type value`

**Статус:** В процессе исправления. Проблема с форматом `conferenceData`.

## Текущий статус

- ✅ Кэш обновляется автоматически
- ✅ Google Calendar сервис инициализирован
- ⚠️ Создание Google Meet ссылок требует доработки формата `conferenceData`

## Тестовый скрипт

Создан `apps/api/test_google_meet.py` для тестирования создания Google Meet ссылок.

Запуск:
```bash
cd apps/api
python test_google_meet.py
```

## Следующие шаги

1. Исправить формат `conferenceData` для Google Meet
2. Протестировать создание реальных ссылок
3. Убедиться, что ссылки работают для участников

