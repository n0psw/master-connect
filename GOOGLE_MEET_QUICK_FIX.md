# 🔧 Быстрое исправление Google Meet

## ✅ Что уже сделано:

1. **Библиотеки установлены:** ✅
   - `google-api-python-client`
   - `google-auth`
   - `google-auth-httplib2`
   - `google-auth-oauthlib`

2. **Credentials файл:** ✅
   - `credentials/masterconnect-478812-2f68ba47d375.json`

3. **Код интеграции:** ✅
   - Реализован в `apps/api/src/integrations/google_calendar.py`
   - Вызывается при подтверждении бронирования

## ⚠️ Текущая проблема:

**Интеграция отключена** - нужно проверить настройки в `.env`

## 🔧 Что нужно сделать:

### 1. Проверить `.env` файл в `apps/api/`:

Должны быть следующие строки:
```env
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_SERVICE_ACCOUNT_FILE=C:/Users/ultua/PycharmProjects/masterconnect/credentials/masterconnect-478812-2f68ba47d375.json
GOOGLE_CALENDAR_ID=ultuac@gmail.com
```

### 2. Проверить доступ Service Account к календарю:

1. Откройте JSON файл: `credentials/masterconnect-478812-2f68ba47d375.json`
2. Найдите поле `"client_email"` (например: `masterconnect-calendar@project-id.iam.gserviceaccount.com`)
3. Откройте Google Calendar: https://calendar.google.com/
4. Настройки → Общий доступ
5. Добавьте email из `client_email` с правами **"Изменение мероприятий"**

### 3. Перезапустить backend:

```bash
cd apps/api
python run_server.py
```

### 4. Проверить логи при запуске:

Должно быть:
```
Google Calendar service initialized with Service Account (file)
Google Calendar service initialized successfully
```

Если ошибка:
```
Google Calendar service not initialized: missing credentials
```
→ Проверьте путь к файлу в `.env`

Если ошибка:
```
Failed to load Service Account file: ...
```
→ Проверьте, что файл существует и доступен

## 🧪 Тестирование:

1. **Создать тестовое бронирование:**
   - Студент создает бронирование
   - Отмечает оплату
   - Админ подтверждает

2. **Проверить в базе:**
   ```sql
   SELECT meeting_url, meeting_event_id 
   FROM bookings 
   WHERE status = 'CONFIRMED' 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```

3. **Проверить в Google Calendar:**
   - Зайти в календарь `ultuac@gmail.com`
   - Должно появиться событие с Google Meet ссылкой

## 📝 Статус:

- ✅ Библиотеки установлены
- ✅ Credentials файл есть
- ⚠️ Нужно проверить настройки `.env`
- ⚠️ Нужно проверить доступ Service Account к календарю
- ⚠️ Нужно перезапустить backend

## 🔗 Документация:

Полная инструкция: `GOOGLE_MEET_SETUP.md`
Статус интеграции: `GOOGLE_MEET_STATUS.md`

