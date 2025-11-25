# Пошаговая инструкция по деплою MasterConnect

## Что уже сделано ✅

1. ✅ Проект загружен на GitHub: `https://github.com/n0psw/master-connect.git`
2. ✅ Все ненужные файлы удалены из репозитория
3. ✅ Docker конфигурация готова
4. ✅ Nginx конфиги созданы

## Что нужно сделать на сервере

### 1. Подключиться к серверу и клонировать репозиторий

```bash
ssh user@your-server-ip
cd /opt  # или /var/www или другая директория
git clone https://github.com/n0psw/master-connect.git
cd master-connect
```

### 2. Создать .env файл

```bash
cp .env.production.example .env
nano .env
```

**Обязательно заполните:**

```env
# Сгенерируйте секретные ключи:
# openssl rand -hex 32
SECRET_KEY=ваш-секретный-ключ-32-символа
JWT_SECRET_KEY=ваш-jwt-секретный-ключ-32-символа

# База данных
DATABASE_URL=postgresql+psycopg://postgres:ВАШ_ПАРОЛЬ@postgres:5432/masterconnect
POSTGRES_PASSWORD=ВАШ_НАДЕЖНЫЙ_ПАРОЛЬ

# CORS - ваш домен
BACKEND_CORS_ORIGINS=https://masterconnect.mastereducation.kz

# API URL для фронтенда (важно!)
VITE_API_URL=https://api.masterconnect.mastereducation.kz/api/v1
VITE_WS_URL=wss://api.masterconnect.mastereducation.kz/ws

# Остальные настройки (S3, Email, Google Calendar)
# Заполните по необходимости
```

### 3. Выбрать вариант настройки Nginx

#### Вариант A: Отдельные домены для MasterConnect

Если у вас есть отдельные домены:
- `masterconnect.mastereducation.kz` - для фронтенда
- `api.masterconnect.mastereducation.kz` - для API

```bash
# Скопировать конфиг
sudo cp nginx/masterconnect.conf /etc/nginx/sites-available/masterconnect
sudo ln -s /etc/nginx/sites-available/masterconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Вариант B: Использовать существующий API Gateway

Если хотите использовать `api.mastereducation.kz`:

```bash
# Отредактировать существующий конфиг
sudo nano /etc/nginx/sites-enabled/api_gateway.conf
```

Добавить в секцию `server { listen 80; server_name api.mastereducation.kz ... }`:

```nginx
# --- MasterConnect API ---
location /masterconnect/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    client_max_body_size 10M;
}
```

И обновить в `.env`:
```
VITE_API_URL=https://api.mastereducation.kz/masterconnect/api/v1
VITE_WS_URL=wss://api.mastereducation.kz/masterconnect/ws
```

### 4. Собрать и запустить Docker контейнеры

```bash
# Сборка (может занять время)
docker-compose build

# Запуск
docker-compose up -d

# Проверка статуса
docker-compose ps

# Должны быть запущены:
# - masterconnect_postgres (healthy)
# - masterconnect_redis (healthy)
# - masterconnect_api (healthy)
# - masterconnect_web
# - masterconnect_celery
# - masterconnect_celery_beat
```

### 5. Применить миграции базы данных

```bash
docker-compose exec api alembic upgrade head
```

### 6. Проверить работу

```bash
# Проверка API
curl http://localhost:8000/health

# Проверка логов
docker-compose logs -f api
```

### 7. Настроить SSL (после проверки работы)

```bash
# Для отдельных доменов
sudo certbot --nginx -d masterconnect.mastereducation.kz -d api.masterconnect.mastereducation.kz

# Или для API Gateway (если используете вариант B)
# SSL уже должен быть настроен для api.mastereducation.kz
```

### 8. Создать первого администратора

```bash
# Через API (после запуска)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password",
    "full_name": "Admin User"
  }'

# Затем через админку или напрямую в БД изменить роль на ADMIN
```

## Важные моменты

1. **Порты:**
   - API: `8000` (внутри Docker, проксируется через Nginx)
   - Web: `3000` (внутри Docker, проксируется через Nginx)
   - PostgreSQL: `5432` (только внутри Docker сети)
   - Redis: `6379` (только внутри Docker сети)

2. **Переменные окружения:**
   - `VITE_API_URL` и `VITE_WS_URL` используются при **сборке** фронтенда
   - После изменения этих переменных нужно **пересобрать** контейнер web:
     ```bash
     docker-compose build web
     docker-compose up -d web
     ```

3. **База данных:**
   - PostgreSQL создается автоматически в Docker volume
   - Данные сохраняются в `postgres_data` volume
   - Для бэкапа: `docker-compose exec postgres pg_dump -U postgres masterconnect > backup.sql`

4. **Файлы uploads:**
   - Сохраняются в `./uploads/` на хосте
   - Доступны через `/uploads/` в API

## Troubleshooting

### Проблема: Контейнеры не запускаются

```bash
# Проверить логи
docker-compose logs

# Проверить .env файл
cat .env | grep -v PASSWORD

# Проверить порты
netstat -tulpn | grep -E "8000|3000|5432"
```

### Проблема: API не отвечает

```bash
# Проверить что контейнер запущен
docker-compose ps api

# Проверить логи
docker-compose logs api

# Проверить подключение к БД
docker-compose exec api python -c "from src.core.config import settings; print(settings.DATABASE_URL)"
```

### Проблема: Фронтенд не подключается к API

1. Проверить `VITE_API_URL` в `.env`
2. Пересобрать контейнер web:
   ```bash
   docker-compose build web
   docker-compose up -d web
   ```
3. Проверить Nginx конфиг
4. Проверить CORS настройки в `.env` (BACKEND_CORS_ORIGINS)

## Обновление приложения

```bash
cd /opt/master-connect
git pull
docker-compose build
docker-compose up -d
docker-compose exec api alembic upgrade head
```

