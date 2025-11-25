# Настройка PostgreSQL для MasterConnect

## Автоматическое создание базы данных

**Хорошая новость:** База данных создается **автоматически** при первом запуске PostgreSQL контейнера!

В `docker-compose.yml` уже настроено:
```yaml
postgres:
  environment:
    POSTGRES_DB: ${POSTGRES_DB:-masterconnect}  # База создается автоматически
    POSTGRES_USER: ${POSTGRES_USER:-postgres}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
```

## Шаги для запуска:

### 1. Создай `.env` файл
```bash
# Скопируй пример для локальной разработки
cp env.local.example .env
```

### 2. Настрой `.env` файл
Открой `.env` и убедись, что есть эти строки:
```env
# База данных PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/masterconnect
POSTGRES_DB=masterconnect
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 3. Запусти PostgreSQL
```bash
docker compose up -d postgres
```

База данных `masterconnect` будет создана автоматически!

### 4. Проверь, что база создана
```bash
# Подключись к PostgreSQL
docker compose exec postgres psql -U postgres -l

# Должна быть видна база masterconnect
```

### 5. Примени миграции (если запускаешь API)
```bash
# Запусти API - миграции применятся автоматически при старте
docker compose up -d api
```

## Если нужно создать базу вручную (не требуется, но на всякий случай):

```bash
# Подключись к PostgreSQL
docker compose exec postgres psql -U postgres

# В psql выполни:
CREATE DATABASE masterconnect;
\q
```

## Важно:

- **База создается автоматически** благодаря `POSTGRES_DB` в docker-compose.yml
- Не нужно создавать базу вручную через psql
- Миграции Alembic применяются автоматически при старте API
- Все таблицы создаются через миграции Alembic

