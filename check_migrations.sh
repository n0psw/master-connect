#!/bin/bash

echo "🔍 Проверка состояния миграций на сервере..."
echo ""

# 1. Проверяем, какие файлы миграций есть в контейнере
echo "1️⃣ Файлы миграций в контейнере:"
docker compose exec api ls -la /app/alembic/versions/ | grep "2025_11_25"

echo ""
echo "2️⃣ Текущая версия миграции в базе данных:"
docker compose exec api alembic current

echo ""
echo "3️⃣ История миграций (последние 5):"
docker compose exec api alembic history | head -10

echo ""
echo "4️⃣ Проверяем таблицы в базе данных:"
echo "   - mentor_settings:"
docker compose exec postgres psql -U postgres -d masterconnect -c "\d mentor_settings" 2>&1 | head -5

echo "   - notifications:"
docker compose exec postgres psql -U postgres -d masterconnect -c "\d notifications" 2>&1 | head -5

echo ""
echo "5️⃣ Проверяем версию Alembic в базе данных:"
docker compose exec postgres psql -U postgres -d masterconnect -c "SELECT * FROM alembic_version;" 2>&1

echo ""
echo "✅ Проверка завершена."

