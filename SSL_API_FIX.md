# Исправление SSL для API

## Проблема
Фронтенд работает на HTTPS, но API URL указывает на HTTP, что вызывает ошибку `ERR_SSL_UNRECOGNIZED_NAME_ALERT` - браузер блокирует смешанный контент.

## Решение

### 1. Обновите `.env` файл

Замените HTTP на HTTPS для API URL:

```bash
# Было:
VITE_API_URL=http://apiconnect.mastereducation.kz/api/v1
VITE_WS_URL=ws://apiconnect.mastereducation.kz/ws

# Стало:
VITE_API_URL=https://apiconnect.mastereducation.kz/api/v1
VITE_WS_URL=wss://apiconnect.mastereducation.kz/ws
```

Также обновите `BACKEND_CORS_ORIGINS` в `.env`:

```bash
BACKEND_CORS_ORIGINS=https://connect.mastereducation.kz,https://www.connect.mastereducation.kz,https://apiconnect.mastereducation.kz
```

### 2. Перезапустите API контейнер

Это подключит API к сети proxy и nginx-proxy автоматически получит SSL сертификат:

```bash
docker compose up -d api
```

### 3. Пересоберите web контейнер

Чтобы применить новый HTTPS API URL:

```bash
docker compose build web
docker compose up -d web
```

### 4. Проверьте работу

Подождите 1-2 минуты пока nginx-proxy получит SSL сертификат для `apiconnect.mastereducation.kz`, затем проверьте:

```bash
# Проверьте HTTPS для API
curl -I https://apiconnect.mastereducation.kz/api/v1/health

# Проверьте логи nginx-proxy-acme (сертификат должен быть получен)
docker logs nginx-proxy-acme --tail 50 | grep apiconnect

# Проверьте, что web контейнер использует HTTPS URL
docker exec -it masterconnect_web env | grep VITE_API_URL
```

### 5. Если что-то пошло не так

Если SSL сертификат не получен, проверьте логи:

```bash
# Логи nginx-proxy-acme
docker logs nginx-proxy-acme --tail 100

# Логи nginx-proxy
docker logs nginx-proxy --tail 50

# Проверьте, что API контейнер в сети proxy
docker network inspect proxy | grep masterconnect_api
```

## Результат

После выполнения всех шагов:
- Фронтенд будет обращаться к API через HTTPS
- SSL сертификат будет автоматически получен и обновляться
- Браузер не будет блокировать запросы (нет смешанного контента)

