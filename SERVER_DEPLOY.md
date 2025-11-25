# Инструкция по деплою MasterConnect на сервер

## Шаг 1: Подключение к серверу и клонирование репозитория

```bash
ssh user@your-server-ip
cd /opt  # или другая директория для проектов
git clone https://github.com/n0psw/master-connect.git
cd master-connect
```

## Шаг 2: Создание .env файла

```bash
cp .env.production.example .env
nano .env  # или vi .env
```

### Обязательные настройки в .env:

```env
# Основные настройки
APP_ENV=production
DEBUG=false
SECRET_KEY=<сгенерируйте: openssl rand -hex 32>
JWT_SECRET_KEY=<сгенерируйте: openssl rand -hex 32>

# База данных PostgreSQL
DATABASE_URL=postgresql+psycopg://postgres:YOUR_STRONG_PASSWORD@postgres:5432/masterconnect
POSTGRES_DB=masterconnect
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD

# Redis
REDIS_URL=redis://redis:6379/0

# CORS - укажите ваш домен
BACKEND_CORS_ORIGINS=https://connect.mastereducation.kz,https://www.connect.mastereducation.kz

# Остальные настройки (S3, Email, Google Calendar и т.д.)
# Заполните согласно .env.production.example
```

## Шаг 3: Настройка переменных окружения для фронтенда

Добавьте в корневой `.env` файл переменные для сборки фронтенда:

```bash
# В корневом .env файле добавьте:
VITE_API_URL=https://api.masterconnect.mastereducation.kz/api/v1
VITE_WS_URL=wss://api.masterconnect.mastereducation.kz/ws
```

**Важно:** 
- Замените домены на ваши реальные!
- Для HTTP используйте `http://` и `ws://`
- Для HTTPS используйте `https://` и `wss://`
- Эти переменные передаются в Dockerfile при сборке фронтенда

## Шаг 4: Сборка и запуск Docker контейнеров

```bash
# Сборка образов
docker-compose build

# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f api
```

## Шаг 5: Применение миграций базы данных

```bash
docker-compose exec api alembic upgrade head
```

## Шаг 6: Создание администратора (опционально)

```bash
docker-compose exec api python -c "
from src.modules.users.domain.models import User
from src.modules.auth.application.services import AuthService
from src.db.session import SessionLocal
import asyncio

async def create_admin():
    async with SessionLocal() as db:
        auth_service = AuthService(db)
        # Создайте админа через API или вручную
        print('Use API endpoint to create admin')

asyncio.run(create_admin())
"
```

Или используйте существующий скрипт (если он есть в репозитории).

## Шаг 7: Настройка Nginx

### Вариант 1: Отдельный домен для MasterConnect

Создайте конфиг для MasterConnect:

```bash
sudo nano /etc/nginx/sites-available/masterconnect
```

Скопируйте содержимое из `nginx/masterconnect.conf`.

Активируйте конфиг:

```bash
sudo ln -s /etc/nginx/sites-available/masterconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Вариант 2: Добавить в существующий API Gateway

Если хотите использовать существующий API Gateway (`api.mastereducation.kz`), добавьте в `/etc/nginx/sites-enabled/api_gateway.conf`:

```nginx
# В секцию server { listen 80; server_name api.mastereducation.kz ... }
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

Тогда API будет доступен по: `https://api.mastereducation.kz/masterconnect/api/v1`

И обновите `VITE_API_URL` в `.env`:
```
VITE_API_URL=https://api.mastereducation.kz/masterconnect/api/v1
```

## Шаг 8: Настройка SSL (Let's Encrypt)

```bash
sudo certbot --nginx -d masterconnect.mastereducation.kz -d api.masterconnect.mastereducation.kz
```

## Шаг 9: Проверка работы

- Откройте в браузере: `https://masterconnect.mastereducation.kz`
- Проверьте API: `https://api.masterconnect.mastereducation.kz/health`
- Проверьте логи: `docker-compose logs -f`

## Обновление приложения

```bash
cd /opt/master-connect
git pull
docker-compose build
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## Полезные команды

```bash
# Остановка
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart api

# Просмотр логов
docker-compose logs -f api
docker-compose logs -f web

# Бэкап БД
docker-compose exec postgres pg_dump -U postgres masterconnect > backup_$(date +%Y%m%d).sql

# Восстановление БД
docker-compose exec -T postgres psql -U postgres masterconnect < backup.sql
```

