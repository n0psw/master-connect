# Полный план настройки SSL для MasterConnect

## Текущая ситуация:

✅ **Frontend** (`connect.mastereducation.kz`) - в nginx-proxy, добавлены переменные SSL  
✅ **API** через API Gateway (`api.mastereducation.kz/connect/`) - нужно настроить SSL для API Gateway  
❌ **Проблема:** `api.mastereducation.kz` указывает на другой IP, не на этот сервер!

---

## План действий:

### Шаг 1: SSL для Frontend (connect.mastereducation.kz)

✅ **УЖЕ СДЕЛАНО:** Добавлены переменные `LETSENCRYPT_HOST` и `LETSENCRYPT_EMAIL` в `docker-compose.yml`

**Что делать:**
```bash
# Перезапусти web контейнер, чтобы применить изменения
cd ~/projects/master-connect
docker compose up -d --build web

# Проверь, что nginx-proxy увидел изменения
docker exec -it nginx-proxy cat /etc/nginx/conf.d/default.conf | grep "connect.mastereducation.kz"

# Через несколько минут (nginx-proxy-acme получит сертификат автоматически)
docker exec -it nginx-proxy ls -la /etc/nginx/certs/ | grep connect
```

**Время:** nginx-proxy-acme получит сертификат автоматически в течение 5-10 минут.

---

### Шаг 2: SSL для API Gateway

**Проблема:** `api.mastereducation.kz` указывает на другой сервер (`185.129.51.146`), а API Gateway находится здесь (`185.129.48.238`).

**Вариант A: Использовать `apiconnect.mastereducation.kz` для API**

1. Добавить `apiconnect.mastereducation.kz` в API Gateway конфиг
2. Настроить SSL для этого домена

**Вариант B: Настроить SSL для `api.mastereducation.kz` на этом сервере**

1. Изменить DNS запись `api.mastereducation.kz` → `185.129.48.238` (этот сервер)
2. Настроить SSL для `api.mastereducation.kz`

**Вариант C: Использовать nginx-proxy для API**

1. Добавить API контейнер в nginx-proxy с доменом `apiconnect.mastereducation.kz`
2. SSL настроится автоматически

---

## Рекомендация: Вариант A или C

Поскольку `apiconnect.mastereducation.kz` уже указывает на этот сервер, лучше использовать его.

### Вариант A: Через API Gateway на хосте

**1. Обновить API Gateway конфиг:**

```bash
sudo nano /etc/nginx/sites-available/api-gateway.conf
```

**Добавить `apiconnect.mastereducation.kz` в server_name:**

```nginx
server {
    listen 80;
    server_name api.mastereducation.kz lmsapi.mastereducation.kz apiconnect.mastereducation.kz;
    # ... остальное без изменений ...
}
```

**2. Получить SSL сертификат:**

```bash
# Создай директорию для ACME challenge
sudo mkdir -p /var/www/letsencrypt

# Добавь location для ACME challenge в API Gateway (перед другими location):
sudo nano /etc/nginx/sites-available/api-gateway.conf
```

**Добавить в начало server блока:**

```nginx
server {
    listen 80;
    server_name api.mastereducation.kz lmsapi.mastereducation.kz apiconnect.mastereducation.kz;
    client_max_body_size 5M;

    # ACME challenge для Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    # ... остальные location ...
}
```

**3. Получить сертификат:**

```bash
# Проверь конфиг
sudo nginx -t

# Перезагрузи Nginx
sudo systemctl reload nginx

# Получи сертификат
sudo certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d apiconnect.mastereducation.kz \
  --email admin@mastereducation.kz \
  --agree-tos \
  --non-interactive

# Если нужно для всех доменов:
sudo certbot certonly --webroot \
  -w /var/www/letsencrypt \
  -d api.mastereducation.kz \
  -d lmsapi.mastereducation.kz \
  -d apiconnect.mastereducation.kz \
  --email admin@mastereducation.kz \
  --agree-tos \
  --non-interactive
```

**4. Добавить HTTPS блок в API Gateway:**

См. следующий шаг.

---

### Вариант C: Через nginx-proxy (проще)

**1. Подключить API контейнер к сети proxy:**

```bash
docker network connect proxy masterconnect_api
```

**2. Обновить docker-compose.yml:**

Добавить переменные окружения для API:

```yaml
api:
  # ... существующие настройки ...
  environment:
    - VIRTUAL_HOST=apiconnect.mastereducation.kz
    - VIRTUAL_PORT=8000
    - LETSENCRYPT_HOST=apiconnect.mastereducation.kz
    - LETSENCRYPT_EMAIL=admin@mastereducation.kz
  networks:
    - masterconnect
    - proxy  # ДОБАВИТЬ!
```

**3. Перезапустить API:**

```bash
docker compose up -d api
```

**4. SSL получится автоматически!** 🎉

---

## Рекомендация: Использовать Вариант C (через nginx-proxy)

Это проще и автоматичнее. Но нужно:
1. Убрать проброс порта `8000` из API контейнера (или оставить для локального доступа)
2. Обновить `.env` чтобы использовать `apiconnect.mastereducation.kz`

---

## Обновление .env после настройки SSL

```bash
# Обновить VITE_API_URL и VITE_WS_URL
VITE_API_URL=https://apiconnect.mastereducation.kz/api/v1
VITE_WS_URL=wss://apiconnect.mastereducation.kz/ws

# Или если через API Gateway:
VITE_API_URL=https://api.mastereducation.kz/connect/api/v1
VITE_WS_URL=wss://api.mastereducation.kz/connect/ws
```

---

## Что делать СЕЙЧАС:

1. ✅ **Frontend SSL:** Перезапусти web контейнер (переменные уже добавлены)
2. ❓ **API SSL:** Выбери вариант (A или C) - рекомендую C
3. ✅ **Обнови .env:** После настройки SSL обнови URLs на HTTPS

---

## Команды для быстрой проверки:

```bash
# 1. Перезапусти web для применения SSL переменных
cd ~/projects/master-connect
docker compose up -d web

# 2. Проверь, появился ли домен в nginx-proxy
docker exec -it nginx-proxy cat /etc/nginx/conf.d/default.conf | grep connect.mastereducation.kz

# 3. Через 5-10 минут проверь сертификат
docker exec -it nginx-proxy ls -la /etc/nginx/certs/ | grep connect

# 4. Проверь HTTPS
curl -I https://connect.mastereducation.kz 2>&1 | head -3
```

---

## Какой вариант выбираем для API?

- **Вариант A:** API Gateway на хосте (нужно настраивать SSL вручную)
- **Вариант C:** nginx-proxy (автоматический SSL через переменные окружения)

Рекомендую **Вариант C** - проще и автоматичнее!

