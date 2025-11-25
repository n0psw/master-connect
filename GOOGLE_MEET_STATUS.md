# Статус интеграции Google Meet

## ✅ Что настроено:

1. **Credentials файл:** ✅ Найден
   - Путь: `credentials/masterconnect-478812-2f68ba47d375.json`

2. **Переменные окружения:** ✅ Настроены
   ```
   GOOGLE_CALENDAR_ENABLED=true
   GOOGLE_SERVICE_ACCOUNT_FILE=C:/Users/ultua/PycharmProjects/masterconnect/credentials/masterconnect-478812-2f68ba47d375.json
   GOOGLE_CALENDAR_ID=ultuac@gmail.com
   ```

3. **Код интеграции:** ✅ Реализован
   - `apps/api/src/integrations/google_calendar.py` - сервис Google Calendar
   - `apps/api/src/modules/bookings/application/services.py` - создание событий при подтверждении

## 🔄 Как это работает:

### При создании бронирования:

1. **Студент создает бронирование** → статус `HOLD`
2. **Студент отмечает оплату** → статус `AWAITING_VERIFICATION`
3. **Админ подтверждает оплату** → статус `CONFIRMED`
4. **При подтверждении (`CONFIRMED`):**
   - Вызывается `_create_calendar_event(booking)`
   - Создается событие в Google Calendar
   - Google автоматически генерирует Google Meet ссылку
   - Ссылка сохраняется в `booking.meeting_url`
   - Event ID сохраняется в `booking.meeting_event_id`
   - Приглашения отправляются на email студента и ментора

### Код создания события:

```python
# apps/api/src/modules/bookings/application/services.py:674
try:
    calendar_event = await self._create_calendar_event(booking)
    booking.meeting_event_id = calendar_event.event_id
    booking.meeting_url = calendar_event.meet_link
    logger.info("Calendar event created successfully", ...)
except Exception as e:
    logger.error("Failed to create calendar event, but booking will be confirmed", ...)
    # Бронирование подтверждается даже если календарь недоступен
```

## ⚠️ Важные моменты:

1. **Google Meet создается ТОЛЬКО при подтверждении (`CONFIRMED`)**
   - Не создается при `HOLD` или `AWAITING_VERIFICATION`
   - Создается автоматически при переходе в `CONFIRMED`

2. **Если Google Calendar недоступен:**
   - Бронирование все равно подтверждается
   - Ошибка логируется, но не блокирует процесс
   - В dev режиме возвращается тестовая ссылка

3. **Требования:**
   - Service Account должен иметь доступ к календарю `ultuac@gmail.com`
   - Права: "Изменение мероприятий" (Edit events)
   - Email из `client_email` в JSON должен быть добавлен в календарь

## 🧪 Как проверить:

1. **Создать тестовое бронирование:**
   - Зайти как студент
   - Забронировать консультацию
   - Отметить оплату
   - Админ подтверждает

2. **Проверить в базе:**
   ```sql
   SELECT id, status, meeting_url, meeting_event_id 
   FROM bookings 
   WHERE status = 'CONFIRMED' 
   ORDER BY created_at DESC 
   LIMIT 5;
   ```

3. **Проверить в Google Calendar:**
   - Зайти в календарь `ultuac@gmail.com`
   - Должно появиться событие с Google Meet ссылкой

4. **Проверить логи backend:**
   - Должно быть: `"Calendar event created successfully"`
   - Или ошибка, если что-то не так

## 🔧 Если не работает:

1. **Проверить доступность сервиса:**
   ```python
   from integrations.google_calendar import google_calendar_service
   print(google_calendar_service.is_available())  # Должно быть True
   ```

2. **Проверить логи:**
   - `"Google Calendar service initialized successfully"` - OK
   - `"Google Calendar service not initialized: missing credentials"` - проблема с credentials
   - `"Failed to create Google Calendar event"` - проблема с доступом к календарю

3. **Проверить доступ Service Account:**
   - Открыть Google Calendar
   - Настройки → Общий доступ
   - Убедиться, что email из `client_email` добавлен с правами "Изменение мероприятий"

4. **Проверить Calendar ID:**
   - Должен быть `ultuac@gmail.com` или `primary`
   - Можно использовать специальный Calendar ID из настроек

## 📝 Документация:

Полная инструкция по настройке: `GOOGLE_MEET_SETUP.md`

