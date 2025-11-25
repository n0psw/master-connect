#!/bin/bash
# Скрипт для копирования миграций в контейнер без пересборки

echo "Копирую файлы миграций в контейнер..."

# Копируем файлы миграций напрямую в контейнер
docker cp apps/api/alembic/versions/2025_11_25_1700-add_mentor_settings_table.py masterconnect_api:/app/alembic/versions/
docker cp apps/api/alembic/versions/2025_11_25_1701-add_notifications_table.py masterconnect_api:/app/alembic/versions/

echo "Проверяю, что файлы скопированы..."
docker compose exec api ls -la /app/alembic/versions/ | grep "2025_11_25_17"

echo "Проверяю историю миграций..."
docker compose exec api alembic history | tail -5

echo "Применяю миграции..."
docker compose exec api alembic upgrade head

echo "Проверяю таблицы..."
docker compose exec postgres psql -U postgres -d masterconnect -c "\d mentor_settings" || echo "Таблица mentor_settings не найдена"
docker compose exec postgres psql -U postgres -d masterconnect -c "\d notifications" || echo "Таблица notifications не найдена"

echo "Готово!"

