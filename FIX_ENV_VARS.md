# Исправление переменных окружения для API

## Проблема
Переменные окружения `VIRTUAL_HOST` и `LETSENCRYPT_HOST` не применяются к API контейнеру.

## Решение

Проверьте на сервере, что в docker-compose.yml есть секция environment для API:

```bash
# Проверьте, есть ли переменные в docker-compose.yml
grep -A 5 "environment:" docker-compose.yml | head -20

# Или посмотрите секцию api полностью
sed -n '/^  api:/,/^  [a-z]/p' docker-compose.yml | head -30
```

Если переменных нет в файле, добавьте их или обновите файл на сервере из репозитория.

Если переменные есть, но не применяются, попробуйте установить их напрямую при создании контейнера:

```bash
# Удалите контейнер
docker compose stop api
docker compose rm -f api

# Создайте контейнер с переменными напрямую
docker run -d \
  --name masterconnect_api \
  --network masterconnect \
  --network proxy \
  -e VIRTUAL_HOST=apiconnect.mastereducation.kz \
  -e VIRTUAL_PORT=8000 \
  -e LETSENCRYPT_HOST=apiconnect.mastereducation.kz \
  -e LETSENCRYPT_EMAIL=admin@mastereducation.kz \
  --env-file .env \
  -p 8000:8000 \
  master-connect-api

# Или используйте docker compose с явным указанием переменных
docker compose up -d api
```

