# 🔍 Отладка Google Meet - Почему ссылки dev-

## Проблема

Создаются ссылки вида: `https://meet.google.com/dev-431ac1e1-cbc6-40f3-baba-feef88537192`

Это означает, что `google_calendar_service.is_available()` возвращает `False`.

## Причины

### 1. Service Account не добавлен к календарю

**Проверка:**
1. Откройте: https://calendar.google.com/
2. Настройки → Общий доступ
3. Проверьте, есть ли: `masterconnect-calendar@masterconnect-478812.iam.gserviceaccount.com`

**Если НЕТ:**
- Добавьте email
- Права: **"Изменение мероприятий"** (Make changes to events)
- Сохраните

### 2. Ошибка при создании события

**Проверьте логи backend** при подтверждении бронирования:

```
Google Calendar API error: ...
```

**Частые ошибки:**
- `403 Forbidden` → Service Account не имеет доступа
- `404 Not Found` → Неправильный Calendar ID
- `401 Unauthorized` → Проблемы с credentials

### 3. Сервис не инициализирован

**Проверьте логи при старте backend:**

**Должно быть:**
```
Google Calendar service initialized with Service Account (file)
Google Calendar service initialized successfully
```

**Если НЕТ:**
- Проверьте путь к credentials файлу в `.env`
- Проверьте, что файл существует
- Проверьте формат JSON файла

## Как проверить

### Шаг 1: Проверить логи backend

При подтверждении бронирования смотрите логи:

**Если видите:**
```
Google Calendar integration is not available
available=True service_exists=False enabled=True
```
→ Сервис не инициализирован

**Если видите:**
```
Google Calendar API error: 403 Forbidden
```
→ Service Account не имеет доступа к календарю

### Шаг 2: Проверить доступ Service Account

1. Откройте Google Calendar
2. Настройки → Общий доступ
3. Должен быть: `masterconnect-calendar@masterconnect-478812.iam.gserviceaccount.com`
4. Права: **"Изменение мероприятий"**

### Шаг 3: Тест создания события

После добавления Service Account:

1. **Перезапустите backend**
2. **Подтвердите бронирование** (админ)
3. **Проверьте логи** - должно быть:
   ```
   Google Calendar event created
   booking_id=... event_id=... meeting_url=...
   ```
4. **Проверьте ссылку** - должна быть реальная:
   ```
   https://meet.google.com/xxx-xxxx-xxx
   ```
   (БЕЗ `dev-`)

## Исправления в коде

Добавлено детальное логирование:

1. **При недоступности сервиса:**
   - Логирует: `available`, `service_exists`, `enabled`
   - Помогает понять, почему сервис недоступен

2. **При ошибке API:**
   - Логирует: `status_code`, `error_details`
   - Помогает понять причину ошибки

## Следующие шаги

1. ✅ Проверьте логи backend при подтверждении бронирования
2. ✅ Добавьте Service Account к календарю (если не добавлен)
3. ✅ Перезапустите backend
4. ✅ Протестируйте создание нового бронирования

---

**После исправления ссылки будут реальными!** 🎉

