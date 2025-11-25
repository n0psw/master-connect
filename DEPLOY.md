# Инструкция по деплою MasterConnect на сервер

## Требования

- Сервер с установленным Docker и Docker Compose
- Git для клонирования репозитория
- Домен (опционально, для production)

## Шаг 1: Подготовка сервера

### Установка Docker и Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/n0psw/master-connect.git
cd master-connect
```

## Шаг 3: Настройка переменных окружения

### Создание .env файла

```bash
cp .env.production.example .env
```

### Редактирование .env файла

Откройте `.env` и заполните все необходимые значения:

**Обязательные настройки:**

1. **SECRET_KEY** - сгенерируйте случайную строку (минимум 32 символа):
   ```bash
   openssl rand -hex 32
   ```

2. **JWT_SECRET_KEY** - сгенерируйте другую случайную строку:
   ```bash
   openssl rand -hex 32
   ```

3. **POSTGRES_PASSWORD** - установите надежный пароль для PostgreSQL

4. **DATABASE_URL** - обновите пароль в URL:
   ```
   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@postgres:5432/masterconnect
   ```

5. **BACKEND_CORS_ORIGINS** - укажите ваш домен:
   ```
   BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

6. **S3 настройки** - если используете S3 для хранения файлов

7. **Email настройки** - настройки SMTP для отправки писем

8. **Google Calendar** - если используете интеграцию:
   - `GOOGLE_SERVICE_ACCOUNT_JSON_B64` - base64-encoded JSON credentials
   - `GOOGLE_CALENDAR_ID` - ID календаря

## Шаг 4: Миграция базы данных

### Вариант 1: Миграция из SQLite в PostgreSQL (если есть существующая БД)

Если у вас есть SQLite база данных (`test.db`), нужно мигрировать данные:

1. Экспорт данных из SQLite:
   ```bash
   sqlite3 test.db .dump > dump.sql
   ```

2. Импорт в PostgreSQL (после запуска контейнеров):
   ```bash
   docker exec -i masterconnect_postgres psql -U postgres -d masterconnect < dump.sql
   ```

**Внимание:** SQLite и PostgreSQL имеют разные типы данных, может потребоваться ручная корректировка.

### Вариант 2: Создание новой базы данных

Если начинаете с нуля, просто запустите миграции:

```bash
docker-compose run --rm api alembic upgrade head
```

## Шаг 5: Запуск приложения

### Сборка и запуск всех сервисов

```bash
docker-compose build
docker-compose up -d
```

### Проверка статуса

```bash
docker-compose ps
```

Все сервисы должны быть в статусе `Up`.

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f api
docker-compose logs -f web
```

## Шаг 6: Применение миграций базы данных

```bash
docker-compose exec api alembic upgrade head
```

## Шаг 7: Создание администратора (опционально)

```bash
docker-compose exec api python -m src.modules.admin.scripts.create_admin
```

Или используйте существующий скрипт:
```bash
docker-compose exec api python create_admin.py
```

## Шаг 8: Настройка Nginx (реверс-прокси, опционально)

Если хотите использовать Nginx как реверс-прокси перед Docker контейнерами:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Шаг 9: Настройка SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Шаг 10: Обновление приложения

При обновлении кода:

```bash
git pull
docker-compose build
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## Полезные команды

### Остановка всех сервисов
```bash
docker-compose down
```

### Остановка с удалением volumes (ОСТОРОЖНО: удалит данные БД)
```bash
docker-compose down -v
```

### Перезапуск конкретного сервиса
```bash
docker-compose restart api
```

### Выполнение команд в контейнере
```bash
docker-compose exec api python -m src.main
```

### Просмотр использования ресурсов
```bash
docker stats
```

### Бэкап базы данных
```bash
docker-compose exec postgres pg_dump -U postgres masterconnect > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Восстановление из бэкапа
```bash
docker-compose exec -T postgres psql -U postgres masterconnect < backup.sql
```

## Troubleshooting

### Проблема: Контейнеры не запускаются

1. Проверьте логи: `docker-compose logs`
2. Проверьте .env файл на наличие всех обязательных переменных
3. Проверьте, что порты не заняты: `netstat -tulpn | grep :8000`

### Проблема: База данных не подключается

1. Проверьте, что PostgreSQL контейнер запущен: `docker-compose ps postgres`
2. Проверьте DATABASE_URL в .env файле
3. Проверьте логи PostgreSQL: `docker-compose logs postgres`

### Проблема: Файлы не загружаются

1. Проверьте права доступа к директории uploads:
   ```bash
   sudo chown -R $USER:$USER uploads/
   chmod -R 755 uploads/
   ```

### Проблема: CORS ошибки

1. Убедитесь, что BACKEND_CORS_ORIGINS содержит правильный домен
2. Перезапустите API контейнер: `docker-compose restart api`

## Мониторинг

### Health checks

- API: `http://yourdomain.com:8000/health`
- Web: `http://yourdomain.com:3000/health`

### Логи

Все логи сохраняются в контейнерах. Для production рекомендуется настроить централизованное логирование (например, через Docker logging driver или внешний сервис).

## Безопасность

1. **Никогда не коммитьте .env файл в Git**
2. **Используйте сильные пароли** для SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD
3. **Настройте firewall** на сервере (откройте только необходимые порты)
4. **Используйте SSL/TLS** для production
5. **Регулярно обновляйте** Docker образы и зависимости
6. **Настройте автоматические бэкапы** базы данных

## Поддержка

При возникновении проблем проверьте:
- Логи контейнеров
- Настройки .env файла
- Статус всех сервисов
- Сетевое подключение между контейнерами

