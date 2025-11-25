#!/bin/bash
# Скрипт для проверки, что все таблицы созданы и API работает

echo "Проверяю таблицы в базе данных..."

# Проверяю mentor_settings
echo -e "\n=== Таблица mentor_settings ==="
docker compose exec postgres psql -U postgres -d masterconnect -c "\d mentor_settings" || echo "❌ Таблица mentor_settings не найдена"

# Проверяю notifications
echo -e "\n=== Таблица notifications ==="
docker compose exec postgres psql -U postgres -d masterconnect -c "\d notifications" || echo "❌ Таблица notifications не найдена"

# Проверяю enum notification_type
echo -e "\n=== Enum notification_type ==="
docker compose exec postgres psql -U postgres -d masterconnect -c "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notification_type');" || echo "❌ Enum notification_type не найден"

# Перезапускаю API для применения изменений
echo -e "\n=== Перезапускаю API ==="
docker compose restart api

# Жду немного, чтобы API запустился
sleep 5

# Проверяю логи API на наличие ошибок
echo -e "\n=== Проверяю логи API (последние 20 строк) ==="
docker compose logs api --tail=20 | grep -i "error\|undefined\|exception" || echo "✅ Ошибок не найдено"

# Проверяю health endpoint
echo -e "\n=== Проверяю health endpoint ==="
curl -s http://localhost:8000/health | head -5 || echo "❌ API не отвечает"

echo -e "\n✅ Проверка завершена!"

