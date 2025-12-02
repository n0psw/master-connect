# План настройки SSL для MasterConnect

## Текущая структура:

1. **API Gateway** (`api.mastereducation.kz`) - Nginx на хосте в `/etc/nginx/sites-available/api-gateway.conf`
2. **Frontend** (`connect.mastereducation.kz`) - через nginx-proxy Docker контейнер
3. **API** проксируется через API Gateway на `/connect/` → `http://127.0.0.1:8000/`

---

## План настройки SSL:

### Шаг 1: Проверка nginx-proxy

Выполни на сервере:
```bash
# Проверяем, какой nginx-proxy используется
docker inspect nginx-proxy --format='{{.Config.Image}}'

# Проверяем volumes (где конфиги и сертификаты)
docker inspect nginx-proxy --format='{{range .Mounts}}{{.Source}} -> {{.Destination}} {{end}}'

# Проверяем, есть ли уже SSL для других доменов
ls -la /etc/letsencrypt/live/ 2>/dev/null || echo "Нет сертификатов"

# Проверяем, установлен ли certbot
which certbot
```

**Пришли мне вывод этих команд**, чтобы понять:
- Какой nginx-proxy используется (jwilder/nginx-proxy или кастомный)
- Где находятся конфиги и сертификаты
- Есть ли уже опыт с SSL на этом сервере

---

### Шаг 2: Подготовка к получению сертификатов

#### 2.1 Для `api.mastereducation.kz` (API Gateway на хосте):

```bash
# Создаём директорию для ACME challenge
sudo mkdir -p /var/www/letsencrypt

# Добавляем location для ACME challenge в API Gateway
# Нужно добавить в /etc/nginx/sites-available/api-gateway.conf:
```

**Добавь в `/etc/nginx/sites-available/api-gateway.conf` перед другими location:**

```nginx
server {
    listen 80;
    server_name api.mastereducation.kz lmsapi.mastereducation.kz;
    client_max_body_size 5M;

    # ACME challenge для Let's Encrypt (ДОБАВИТЬ!)
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    # --- Auth Service  ---
    location /auth/ {
        proxy_pass http://127.0.0.1:8080/;
        # ... остальные настройки ...
    }
    
    # ... остальные location ...
}
```

#### 2.2 Для `connect.mastereducation.kz` (nginx-proxy):

Если используется **jwilder/nginx-proxy**, то просто добавь переменные окружения:

```yaml
# В docker-compose.yml для web контейнера:
environment:
  - VIRTUAL_HOST=connect.mastereducation.kz,www.connect.mastereducation.kz
  - VIRTUAL_PORT=80
  - LETSENCRYPT_HOST=connect.mastereducation.kz,www.connect.mastereducation.kz
  - LETSENCRYPT_EMAIL=your-email@example.com
```

Если **кастомный nginx-proxy**, нужно добавить location для ACME challenge в конфиг контейнера.

---

### Шаг 3: Получение сертификатов через Certbot

#### 3.1 Установка Certbot (если ещё не установлен):

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

#### 3.2 Получение сертификата для `api.mastereducation.kz`:

```bash
# Обновляем конфиг API Gateway (добавляем location для ACME)
sudo nano /etc/nginx/sites-available/api-gateway.conf
# Добавь location /.well-known/acme-challenge/ как показано выше

# Проверяем конфиг
sudo nginx -t

# Перезагружаем Nginx
sudo systemctl reload nginx

# Получаем сертификат (webroot mode, не требует остановки Nginx)
sudo certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d api.mastereducation.kz \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive
```

#### 3.3 Получение сертификата для `connect.mastereducation.kz`:

**Если jwilder/nginx-proxy с letsencrypt-nginx-proxy-companion:**

Контейнер автоматически получит сертификат после добавления переменных окружения.

**Если кастомный nginx-proxy или отдельный Nginx:**

```bash
# Нужно добавить location для ACME в конфиг connect.mastereducation.kz
# Затем:
sudo certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d connect.mastereducation.kz \
  -d www.connect.mastereducation.kz \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive
```

---

### Шаг 4: Настройка HTTPS в конфигах

#### 4.1 API Gateway (`/etc/nginx/sites-available/api-gateway.conf`):

**Добавь HTTPS блок:**

```nginx
# HTTP → HTTPS редирект
server {
    listen 80;
    server_name api.mastereducation.kz lmsapi.mastereducation.kz;
    client_max_body_size 5M;

    # ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    # Редирект всего остального на HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name api.mastereducation.kz lmsapi.mastereducation.kz;
    client_max_body_size 5M;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/api.mastereducation.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.mastereducation.kz/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # --- Connect API ---
    location /connect/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Таймауты
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        proxy_connect_timeout 10s;
        proxy_buffering off;
        
        client_max_body_size 10M;
    }

    # --- Auth Service ---
    location /auth/ {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # --- IELTS ---
    location /ielts/ {
        proxy_pass http://127.0.0.1:2001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # --- LMS ---
    location /lms/ {
        proxy_pass http://127.0.0.1:1004/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Статус API Gateway
    location / {
        return 200 "API Gateway is running\n";
    }
}
```

#### 4.2 Frontend (nginx-proxy):

Если **jwilder/nginx-proxy с letsencrypt-nginx-proxy-companion** - всё автоматически!

Если **кастомный** - нужно добавить HTTPS блок вручную.

---

### Шаг 5: Обновление переменных окружения

После настройки SSL обнови `.env`:

```bash
# Старые значения (HTTP):
VITE_API_URL=http://apiconnect.mastereducation.kz/api/v1
VITE_WS_URL=ws://apiconnect.mastereducation.kz/ws

# Новые значения (HTTPS):
VITE_API_URL=https://api.mastereducation.kz/connect/api/v1
VITE_WS_URL=wss://api.mastereducation.kz/connect/ws
```

**ВАЖНО:** После изменения нужно **пересобрать** web контейнер:
```bash
docker compose up -d --build web
```

---

### Шаг 6: Автообновление сертификатов

```bash
# Проверяем, есть ли cron задача для автообновления
sudo crontab -l | grep certbot

# Если нет, добавляем:
sudo crontab -e
# Добавь строку:
0 0,12 * * * certbot renew --quiet --deploy-hook "systemctl reload nginx"
```

---

## Что мне нужно от тебя:

1. **Выполни команды из Шага 1** и пришли вывод
2. **Какой email использовать** для Let's Encrypt (нужен для уведомлений о истечении сертификата)
3. **Есть ли уже SSL** для других доменов на сервере? Если да, покажи как настроено

После этого я дам **точные команды** под твою конфигурацию.

