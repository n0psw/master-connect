# Настройка Google Meet API для создания собраний

## Обзор

Интеграция с Google Calendar API позволяет автоматически создавать Google Meet ссылки при подтверждении бронирования консультаций. Все события создаются в указанном календаре, участники получают приглашения на email.

## Стоимость

**Бесплатно** в пределах лимитов:
- Google Calendar API: 1,000,000 запросов/день (бесплатно)
- Google Meet ссылки: создаются автоматически, бесплатно
- Для большинства проектов этого более чем достаточно

**Требования:**
- Google Cloud проект (бесплатно)
- Биллинг аккаунт (нужен для учета квот, но в пределах free tier платить не нужно)
- Google Workspace НЕ требуется (работает с личными аккаунтами)

## Пошаговая настройка

### Шаг 1: Создание проекта в Google Cloud Console

1. Перейдите на https://console.cloud.google.com/
2. Войдите в свой Google аккаунт
3. Нажмите на селектор проектов вверху → "Создать проект"
4. Укажите название: `MasterConnect` (или другое)
5. Нажмите "Создать" и дождитесь создания

### Шаг 2: Настройка биллинга

1. В меню слева: "Биллинг" (Billing)
2. Нажмите "Связать учетную запись" (Link a billing account)
3. Создайте новую учетную запись:
   - Укажите название
   - Выберите страну
   - Укажите способ оплаты (карта)
   - **Важно:** В пределах free tier платить не нужно, но аккаунт нужен для учета квот

### Шаг 3: Включение Google Calendar API

1. В меню слева: "APIs & Services" → "Библиотека" (Library)
2. В поиске введите: `Google Calendar API`
3. Выберите "Google Calendar API"
4. Нажмите "Включить" (Enable)
5. Дождитесь активации (10-20 секунд)

### Шаг 4: Создание Service Account

1. В меню слева: "APIs & Services" → "Учетные данные" (Credentials)
2. Нажмите "Создать учетные данные" (Create Credentials)
3. Выберите "Service Account" (Сервисный аккаунт)
4. Заполните форму:
   - **Имя:** `masterconnect-calendar` (или другое)
   - **ID:** заполнится автоматически
   - **Описание:** `Service account for MasterConnect calendar integration`
   - Нажмите "Создать и продолжить" (Create and Continue)
5. Роли (опционально):
   - Можно пропустить или выбрать "Editor"
   - Нажмите "Продолжить" (Continue)
6. Пользователи (опционально):
   - Пропустите
   - Нажмите "Готово" (Done)

### Шаг 5: Создание ключа для Service Account

1. В списке Service Accounts откройте созданный аккаунт
2. Перейдите на вкладку "Ключи" (Keys)
3. Нажмите "Добавить ключ" (Add Key) → "Создать новый ключ" (Create new key)
4. Выберите формат: **JSON**
5. Нажмите "Создать" (Create)
6. JSON файл скачается автоматически - **сохраните его в безопасном месте!**
   - Пример имени: `masterconnect-478812-xxxxx.json`
   - **НЕ коммитьте в git!**
   - **НЕ публикуйте!**

### Шаг 6: Предоставление доступа к календарю

1. Откройте скачанный JSON файл
2. Найдите поле `"client_email"` (например: `masterconnect-calendar@project-id.iam.gserviceaccount.com`)
3. Откройте Google Calendar: https://calendar.google.com/
4. Настройки календаря → "Настройки и общий доступ"
5. В разделе "Поделиться с конкретными людьми":
   - Нажмите "Добавить людей"
   - Введите email из `client_email`
   - Выберите права: **"Изменение мероприятий"** (Edit events)
   - Нажмите "Отправить" или "Готово"

**Важно:** Выберите именно "Изменение мероприятий", а не "Доступ ко всем сведениям о мероприятиях" (это только просмотр).

### Шаг 7: Определение Calendar ID

Calendar ID может быть:
- **Email владельца календаря:** `your-email@gmail.com`
- **Специальный ID календаря:** можно найти в настройках календаря в разделе "Интеграция календаря"

Для большинства случаев достаточно использовать email владельца.

## Настройка переменных окружения

Добавьте в `apps/api/.env` файл:

```env
# Включить интеграцию
GOOGLE_CALENDAR_ENABLED=true

# Путь к JSON файлу (для разработки)
GOOGLE_SERVICE_ACCOUNT_FILE=C:/Users/your-username/path/to/service-account.json

# ИЛИ base64-encoded JSON (для production, безопаснее)
# GOOGLE_SERVICE_ACCOUNT_JSON_B64=<base64-encoded-json>

# ID календаря (email владельца или специальный ID)
GOOGLE_CALENDAR_ID=your-email@gmail.com

# Делегированный пользователь (только для Google Workspace)
# GOOGLE_CALENDAR_DELEGATED_USER=mentor@yourdomain.com
```

### Вариант 1: Использование файла (для разработки)

```env
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_SERVICE_ACCOUNT_FILE=C:/Users/ultua/PycharmProjects/masterconnect/credentials/masterconnect-478812-2f68ba47d375.json
GOOGLE_CALENDAR_ID=ultuac@gmail.com
```

### Вариант 2: Использование base64 (для production)

1. Закодируйте JSON файл в base64:
   ```bash
   # Windows PowerShell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("path/to/service-account.json"))
   
   # Linux/Mac
   base64 -i path/to/service-account.json
   ```

2. Добавьте в `.env`:
   ```env
   GOOGLE_CALENDAR_ENABLED=true
   GOOGLE_SERVICE_ACCOUNT_JSON_B64=<результат base64>
   GOOGLE_CALENDAR_ID=your-email@gmail.com
   ```

## Установка зависимостей

Убедитесь, что установлены необходимые библиотеки:

```bash
pip install google-api-python-client google-auth
```

Или они уже должны быть в `requirements.txt`.

## Безопасность

1. **Никогда не коммитьте JSON файлы в git:**
   - Добавьте `credentials/` и `*.json` в `.gitignore`
   - Используйте переменные окружения

2. **Для production:**
   - Используйте base64 в переменных окружения
   - Или используйте Secret Manager (Google Cloud, AWS Secrets Manager и т.д.)
   - Храните credentials в безопасном месте

3. **Права доступа:**
   - Service Account должен иметь только необходимые права
   - Доступ к календарю: "Изменение мероприятий" (не больше)

## Тестирование

1. Запустите сервер:
   ```bash
   cd apps/api
   python -m uvicorn src.main:app --reload
   ```

2. Создайте или подтвердите тестовое бронирование через API

3. Проверьте логи - должно быть сообщение:
   ```
   Google Calendar event created
   ```

4. Проверьте Google Calendar - должно появиться событие с Google Meet ссылкой

5. Проверьте базу данных - поле `meeting_url` должно содержать Google Meet ссылку

6. Проверьте, что ссылка работает - откройте её в браузере

## Как это работает

1. **При подтверждении бронирования:**
   - Платформа создает событие в Google Calendar через Service Account
   - Google автоматически генерирует Google Meet ссылку
   - Приглашения отправляются на email студента и ментора

2. **Участники:**
   - Получают приглашение на email
   - Вид событие в своем календаре (если синхронизирован)
   - Могут присоединиться к Google Meet по ссылке

3. **Клиентам НЕ нужно:**
   - Предоставлять доступ к своим календарям
   - Настраивать что-либо
   - Все работает автоматически

## Устранение неполадок

### Ошибка: "Google Calendar service not initialized: missing credentials"

**Причина:** Не указан путь к JSON файлу или base64.

**Решение:**
- Проверьте, что `GOOGLE_CALENDAR_ENABLED=true`
- Проверьте путь к файлу в `GOOGLE_SERVICE_ACCOUNT_FILE`
- Или укажите `GOOGLE_SERVICE_ACCOUNT_JSON_B64`

### Ошибка: "Failed to create Google Calendar event"

**Причина:** Service Account не имеет доступа к календарю.

**Решение:**
- Проверьте, что Service Account email добавлен в календарь
- Проверьте, что права установлены на "Изменение мероприятий"
- Проверьте, что `GOOGLE_CALENDAR_ID` указан правильно

### Google Meet ссылка не создается

**Причина:** Возможно, календарь не поддерживает Google Meet.

**Решение:**
- Убедитесь, что используете Google Calendar (не другой календарь)
- Проверьте, что у календаря есть доступ к Google Meet
- Попробуйте использовать `primary` календарь

### События создаются, но приглашения не приходят

**Причина:** Email участников указан неправильно или не подтвержден.

**Решение:**
- Проверьте, что email студента и ментора указаны правильно
- Убедитесь, что email подтверждены в системе

## Дополнительная информация

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Google Meet API Documentation](https://developers.google.com/meet/api)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)



