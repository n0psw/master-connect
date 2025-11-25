# Быстрая настройка Google Meet

## Что уже сделано

✅ Проект создан в Google Cloud Console  
✅ Google Calendar API включен  
✅ Service Account создан  
✅ JSON ключ скачан  
✅ Доступ к календарю предоставлен  
✅ Код обновлен для поддержки всех функций  

## Что нужно сделать сейчас

### 1. Добавить настройки в `.env` файл

Откройте `apps/api/.env` (или создайте, если его нет) и добавьте:

```env
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_SERVICE_ACCOUNT_FILE=C:/Users/ultua/PycharmProjects/masterconnect/credentials/masterconnect-478812-2f68ba47d375.json
GOOGLE_CALENDAR_ID=ultuac@gmail.com
```

**Важно:** 
- Замените путь к файлу на ваш реальный путь, если отличается
- Замените `ultuac@gmail.com` на email владельца календаря "adil", если отличается

### 2. Перезапустить сервер

```bash
cd apps/api
python -m uvicorn src.main:app --reload
```

### 3. Проверить логи

При запуске должно быть сообщение:
```
Google Calendar service initialized with Service Account (file)
Google Calendar service initialized successfully
```

### 4. Протестировать

1. Создайте или подтвердите тестовое бронирование
2. Проверьте Google Calendar - должно появиться событие
3. Проверьте базу данных - поле `meeting_url` должно содержать Google Meet ссылку

## Если что-то не работает

См. подробную инструкцию в `GOOGLE_MEET_SETUP.md` раздел "Устранение неполадок"



