#!/bin/bash

echo "🧪 Тестирование эндпоинтов, использующих mentor_settings и notifications..."
echo ""

# Получаем токен для демо-ментора
echo "1️⃣ Получаем токен для демо-ментора (mentor@test.com / password123)..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "mentor@test.com", "password": "password123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Не удалось получить токен. Проверь, что демо-аккаунты созданы."
    echo "   Ответ: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Токен получен"
echo ""

# Тестируем эндпоинт, который использует mentor_settings
echo "2️⃣ Тестируем GET /api/v1/availability/my/profile (использует mentor_settings)..."
PROFILE_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/availability/my/profile \
  -H "Authorization: Bearer $TOKEN")

if echo "$PROFILE_RESPONSE" | grep -q "error\|Error\|undefined\|UndefinedTable"; then
    echo "❌ Ошибка при получении профиля:"
    echo "$PROFILE_RESPONSE"
else
    echo "✅ Профиль получен успешно"
    echo "$PROFILE_RESPONSE" | head -20
fi

echo ""
echo "3️⃣ Тестируем GET /api/v1/availability/my/settings (работает с mentor_settings)..."
SETTINGS_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/availability/my/settings \
  -H "Authorization: Bearer $TOKEN")

if echo "$SETTINGS_RESPONSE" | grep -q "error\|Error\|undefined\|UndefinedTable"; then
    echo "❌ Ошибка при получении настроек:"
    echo "$SETTINGS_RESPONSE"
else
    echo "✅ Настройки получены успешно"
    echo "$SETTINGS_RESPONSE"
fi

echo ""
echo "4️⃣ Проверяем, что таблицы существуют в базе данных..."
MENTOR_SETTINGS_COUNT=$(docker compose exec -T postgres psql -U postgres -d masterconnect -t -c "SELECT COUNT(*) FROM mentor_settings;" | tr -d ' ')
NOTIFICATIONS_COUNT=$(docker compose exec -T postgres psql -U postgres -d masterconnect -t -c "SELECT COUNT(*) FROM notifications;" | tr -d ' ')

echo "   - mentor_settings: $MENTOR_SETTINGS_COUNT записей"
echo "   - notifications: $NOTIFICATIONS_COUNT записей"

echo ""
echo "✅ Тестирование завершено!"

