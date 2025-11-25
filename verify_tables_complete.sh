#!/bin/bash

echo "🔍 Проверка полной структуры таблиц..."
echo ""

echo "=== Таблица mentor_settings (полная структура) ==="
docker compose exec postgres psql -U postgres -d masterconnect -c "\d mentor_settings"

echo ""
echo "=== Таблица notifications (полная структура) ==="
docker compose exec postgres psql -U postgres -d masterconnect -c "\d notifications"

echo ""
echo "=== Проверка enum notification_type ==="
docker compose exec postgres psql -U postgres -d masterconnect -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'notification_type') ORDER BY enumsortorder;"

echo ""
echo "=== Проверка API на ошибки (последние 20 строк логов) ==="
docker compose logs api --tail=20 | grep -i "error\|exception\|undefined" || echo "✅ Ошибок не найдено"

echo ""
echo "✅ Проверка завершена."

