# Разборка путаницы с API Gateway и доменами

## Текущая ситуация:

### Домены и IP адреса:
- `apiconnect.mastereducation.kz` → `185.129.48.238` 
- `api.mastereducation.kz` → `185.129.51.146`
- `connect.mastereducation.kz` → ? (нужно проверить)

### В конфигах:

**В `.env`:**
```
VITE_API_URL=http://apiconnect.mastereducation.kz/api/v1
```

**В `docker-compose.yml` для web:**
```yaml
environment:
  - VIRTUAL_HOST=connect.mastereducation.kz
```

**В `/etc/nginx/sites-available/api-gateway.conf` (на хосте):**
```nginx
server_name api.mastereducation.kz lmsapi.mastereducation.kz;
location /connect/ {
    proxy_pass http://127.0.0.1:8000/;  # наш API
}
```

---

## Вопросы для проверки:

### 1. На каком IP находится текущий сервер?

Выполни на сервере:
```bash
# Внешний IP текущего сервера
curl ifconfig.me
# или
hostname -I
```

### 2. Куда должен идти API?

**Вариант A:** API должен идти через `apiconnect.mastereducation.kz`
- Тогда нужно настроить nginx-proxy или отдельный конфиг для этого домена

**Вариант B:** API должен идти через `api.mastereducation.kz/connect/`
- Тогда всё правильно, но нужно исправить `.env`

### 3. Правильно ли настроен API Gateway?

Проверь:
```bash
# Покажи текущий конфиг API Gateway
cat /etc/nginx/sites-available/api-gateway.conf

# Какие домены уже настроены?
grep -r "server_name" /etc/nginx/sites-enabled/

# Проверь, работает ли наш API через API Gateway
curl -I http://api.mastereducation.kz/connect/api/v1/health
```

---

## Возможные варианты настройки:

### Вариант 1: API через `api.mastereducation.kz/connect/` (текущий конфиг)

Если `api.mastereducation.kz` указывает на этот сервер, то:

1. **Конфиг правильный** - API Gateway уже проксирует `/connect/` → `127.0.0.1:8000`
2. **Нужно исправить `.env`:**
   ```bash
   # Было:
   VITE_API_URL=http://apiconnect.mastereducation.kz/api/v1
   
   # Должно быть:
   VITE_API_URL=https://api.mastereducation.kz/connect/api/v1
   ```

### Вариант 2: API через отдельный домен `apiconnect.mastereducation.kz`

Если `apiconnect.mastereducation.kz` должен быть отдельно, то:

1. **Нужно добавить в nginx-proxy** или создать отдельный конфиг
2. **`.env` правильный**, но нужно настроить SSL для этого домена

---

## Что нужно сделать СЕЙЧАС:

### Шаг 1: Проверка текущего IP сервера

```bash
# Внешний IP
curl ifconfig.me

# Или
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### Шаг 2: Проверка DNS записей

```bash
# Какой IP у connect.mastereducation.kz?
nslookup connect.mastereducation.kz

# Куда указывают все домены?
for domain in connect.mastereducation.kz apiconnect.mastereducation.kz api.mastereducation.kz; do
  echo "=== $domain ==="
  nslookup $domain
done
```

### Шаг 3: Проверка работы API Gateway

```bash
# Проверь, доступен ли наш API через API Gateway
curl http://api.mastereducation.kz/connect/api/v1/health

# Проверь, доступен ли через apiconnect
curl http://apiconnect.mastereducation.kz/api/v1/health
```

### Шаг 4: Проверка конфигов

```bash
# Покажи весь конфиг API Gateway
cat /etc/nginx/sites-available/api-gateway.conf

# Какие конфиги активны?
ls -la /etc/nginx/sites-enabled/

# Проверь логи nginx
sudo tail -20 /var/log/nginx/error.log
```

---

## После проверки:

Пришли мне:
1. **IP текущего сервера** (`curl ifconfig.me`)
2. **DNS записи** для всех доменов
3. **Результат** `curl http://api.mastereducation.kz/connect/api/v1/health`
4. **Конфиг** `/etc/nginx/sites-available/api-gateway.conf`

И я скажу:
- ✅ Правильно ли настроен API Gateway
- ✅ Какой домен использовать для API
- ✅ Что исправить в `.env`
- ✅ Как настроить SSL для нужных доменов

