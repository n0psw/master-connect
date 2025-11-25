#!/bin/bash
# Скрипт для исправления миграций с проверкой существования enum

echo "Обновляю файл миграции в контейнере..."

# Копируем исправленный файл миграции
docker cp apps/api/alembic/versions/2025_11_25_1701-add_notifications_table.py masterconnect_api:/app/alembic/versions/

echo "Проверяю текущее состояние миграций..."
docker compose exec api alembic current

echo "Проверяю, существует ли enum notification_type..."
docker compose exec postgres psql -U postgres -d masterconnect -c "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notification_type');"

echo "Проверяю, существует ли таблица mentor_settings..."
docker compose exec postgres psql -U postgres -d masterconnect -c "\d mentor_settings" 2>&1 | head -5

echo "Проверяю, существует ли таблица notifications..."
docker compose exec postgres psql -U postgres -d masterconnect -c "\d notifications" 2>&1 | head -5

echo "Пытаюсь применить миграции..."
docker compose exec api alembic upgrade head

echo "Проверяю финальное состояние таблиц..."
docker compose exec postgres psql -U postgres -d masterconnect -c "\d mentor_settings"
docker compose exec postgres psql -U postgres -d masterconnect -c "\d notifications"

