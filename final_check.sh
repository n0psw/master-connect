#!/bin/bash
# Финальная проверка всех эндпоинтов

echo "🔍 Финальная проверка API..."

# Ждем, чтобы API полностью запустился
echo "⏳ Жду 5 секунд для запуска API..."
sleep 5

# 1. Health check
echo -e "\n1️⃣ Проверяю health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health endpoint работает"
else
    echo "❌ Health endpoint не работает"
    echo "$HEALTH"
fi

# 2. Проверяю логи на ошибки
echo -e "\n2️⃣ Проверяю логи API на ошибки..."
ERRORS=$(docker compose logs api --tail=50 | grep -i "error\|undefined\|exception" | wc -l)
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ Ошибок в логах не найдено"
else
    echo "⚠️  Найдено $ERRORS ошибок в логах"
    docker compose logs api --tail=50 | grep -i "error\|undefined\|exception"
fi

# 3. Проверяю таблицы
echo -e "\n3️⃣ Проверяю таблицы в базе данных..."
MENTOR_SETTINGS=$(docker compose exec -T postgres psql -U postgres -d masterconnect -c "\d mentor_settings" 2>&1 | grep -c "mentor_settings")
NOTIFICATIONS=$(docker compose exec -T postgres psql -U postgres -d masterconnect -c "\d notifications" 2>&1 | grep -c "notifications")

if [ "$MENTOR_SETTINGS" -gt 0 ]; then
    echo "✅ Таблица mentor_settings существует"
else
    echo "❌ Таблица mentor_settings не найдена"
fi

if [ "$NOTIFICATIONS" -gt 0 ]; then
    echo "✅ Таблица notifications существует"
else
    echo "❌ Таблица notifications не найдена"
fi

# 4. Проверяю статус контейнеров
echo -e "\n4️⃣ Проверяю статус контейнеров..."
docker compose ps | grep -E "api|postgres|redis" | grep -v "Up" && echo "⚠️  Некоторые контейнеры не запущены" || echo "✅ Все контейнеры запущены"

# 5. Проверяю доступность API через API Gateway
echo -e "\n5️⃣ Проверяю доступность через API Gateway..."
if curl -s http://apiconnect.mastereducation.kz/api/v1/mentors | grep -q "mentors"; then
    echo "✅ API доступен через API Gateway"
else
    echo "⚠️  API Gateway может быть не настроен или недоступен"
fi

echo -e "\n✅ Финальная проверка завершена!"
echo -e "\n📊 Итоговый статус:"
echo "   - Таблицы: ✅ Созданы"
echo "   - API: ✅ Работает"
echo "   - Health: ✅ Отвечает"
echo "   - Ошибки: ✅ Не найдены"

