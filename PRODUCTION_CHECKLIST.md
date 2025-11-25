# Production Deployment Checklist

## ✅ Проверка конфигурации для продакшена

### 1. Git и .gitignore ✅
- [x] `.gitignore` правильно настроен
- [x] Все чувствительные файлы исключены (.env, credentials, uploads, *.db)
- [x] Примеры конфигурации включены (!.env.example, !.env.production.example)
- [x] Убраны дубликаты и опечатки

### 2. Docker конфигурация ✅
- [x] `docker-compose.yml` настроен для production
- [x] Используется `env_file: .env` для всех сервисов
- [x] Health checks настроены для postgres, redis, api
- [x] Правильные `depends_on` с условиями `service_healthy`
- [x] Volumes для uploads настроены
- [x] Restart policies установлены (`restart: unless-stopped`)

### 3. Dockerfile для API ✅
- [x] Правильные пути копирования файлов
- [x] Копируется `alembic.ini` и `alembic/` для миграций
- [x] Установлен `curl` для healthcheck
- [x] Создаются директории для uploads
- [x] Используется правильный пользователь (app)

### 4. Dockerfile для Web ✅
- [x] Multi-stage build настроен правильно
- [x] Context установлен на `./apps/web`
- [x] Nginx конфигурация копируется
- [x] Правильный путь к собранным файлам

### 5. База данных (PostgreSQL) ✅
- [x] Формат DATABASE_URL правильный: `postgresql+psycopg://user:password@host:port/database`
- [x] PostgreSQL настройки в docker-compose.yml
- [x] Health check для PostgreSQL настроен
- [x] Volume для данных PostgreSQL создан
- [x] Alembic настроен для использования settings.DATABASE_URL
- [x] Миграции будут работать через `docker-compose exec api alembic upgrade head`

### 6. Переменные окружения ✅
- [x] `.env.production.example` создан со всеми необходимыми переменными
- [x] Все обязательные переменные присутствуют:
  - SECRET_KEY
  - JWT_SECRET_KEY
  - DATABASE_URL (PostgreSQL)
  - POSTGRES_PASSWORD
  - REDIS_URL
  - BACKEND_CORS_ORIGINS
  - S3 настройки (если используется)
  - Email настройки
  - Google Calendar настройки (если используется)
  - KASPI_PAYMENT_URL

### 7. Безопасность ✅
- [x] DEBUG=false для production
- [x] APP_ENV=production
- [x] SECRET_KEY и JWT_SECRET_KEY должны быть сгенерированы
- [x] CORS настроен для production доменов
- [x] Security headers в middleware
- [x] .env файл исключен из git

### 8. Документация ✅
- [x] `DEPLOY.md` создан с полной инструкцией
- [x] `.env.production.example` с комментариями
- [x] Инструкции по миграции БД из SQLite в PostgreSQL

## ⚠️ Что нужно сделать перед деплоем:

1. **Создать .env файл на сервере:**
   ```bash
   cp .env.production.example .env
   ```

2. **Сгенерировать секретные ключи:**
   ```bash
   openssl rand -hex 32  # для SECRET_KEY
   openssl rand -hex 32  # для JWT_SECRET_KEY
   ```

3. **Заполнить все переменные в .env:**
   - POSTGRES_PASSWORD - надежный пароль
   - DATABASE_URL - с правильным паролем
   - BACKEND_CORS_ORIGINS - ваш домен
   - Все остальные настройки (S3, Email, Google Calendar и т.д.)

4. **Проверить что все файлы закоммичены:**
   ```bash
   git status
   git add .
   git commit -m "Production configuration ready"
   git push origin main
   ```

5. **На сервере:**
   - Клонировать репозиторий
   - Создать .env файл
   - Запустить: `docker-compose up -d`
   - Применить миграции: `docker-compose exec api alembic upgrade head`

## 🔍 Дополнительные проверки:

### Проверка подключения к БД:
```bash
docker-compose exec api python -c "from src.core.config import settings; print(settings.DATABASE_URL)"
```

### Проверка миграций:
```bash
docker-compose exec api alembic current
docker-compose exec api alembic history
```

### Проверка health checks:
```bash
docker-compose ps
# Все сервисы должны быть "healthy"
```

### Проверка логов:
```bash
docker-compose logs api
docker-compose logs postgres
```

## ✅ Итоговая проверка:

Все настройки для production готовы:
- ✅ .gitignore правильно настроен
- ✅ Docker конфигурация готова
- ✅ PostgreSQL правильно настроен
- ✅ Переменные окружения документированы
- ✅ Документация по деплою создана
- ✅ Безопасность настроена

**Проект готов к деплою на production сервер!**

