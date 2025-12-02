# Проверка настройки других сайтов на сервере

## Команды для проверки:

### 1. Какие сайты/контейнеры работают через nginx-proxy?

```bash
# Все контейнеры с VIRTUAL_HOST
docker ps --format "{{.Names}}" | while read container; do
  echo "=== $container ==="
  docker inspect $container --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E "VIRTUAL_HOST|LETSENCRYPT"
done
```

### 2. Какие конфиги есть в nginx-proxy?

```bash
# Конфиги автоматически сгенерированные
docker exec -it nginx-proxy cat /etc/nginx/conf.d/default.conf

# Или покажи только server blocks
docker exec -it nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A 10 "server_name"
```

### 3. Какие конфиги на хосте (Nginx на сервере)?

```bash
# Все активные конфиги
ls -la /etc/nginx/sites-enabled/

# Содержимое каждого
for config in /etc/nginx/sites-enabled/*; do
  echo "=== $config ==="
  cat $config
  echo ""
done
```

### 4. Какие Docker контейнеры работают?

```bash
# Все контейнеры с их портами
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

### 5. Какие домены уже настроены в nginx-proxy?

```bash
# Покажи все server_name
docker exec -it nginx-proxy cat /etc/nginx/conf.d/default.conf | grep "server_name" | sort | uniq
```

---

## Что искать:

1. **Как настроены другие сайты:**
   - Через nginx-proxy (переменные окружения)?
   - Через конфиги на хосте?
   - Какие домены используют?

2. **Как настроен SSL:**
   - Есть ли уже HTTPS?
   - Через letsencrypt-nginx-proxy-companion?
   - Через certbot?

3. **Структура:**
   - Где находятся конфиги?
   - Как организованы volumes?

---

## Выполни эти команды и пришли вывод:

```bash
# 1. Все контейнеры с их доменами
docker ps --format "table {{.Names}}\t{{.Ports}}" && echo "" && \
for container in $(docker ps --format "{{.Names}}" | grep -v nginx-proxy); do
  echo "=== $container ==="
  docker inspect $container --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E "VIRTUAL_HOST" || echo "Нет VIRTUAL_HOST"
done

# 2. Конфиги nginx-proxy (первые 50 строк)
docker exec -it nginx-proxy head -50 /etc/nginx/conf.d/default.conf

# 3. Активные конфиги на хосте
ls -la /etc/nginx/sites-enabled/

# 4. Один пример конфига (покажи первый)
cat /etc/nginx/sites-enabled/$(ls /etc/nginx/sites-enabled/ | head -1) 2>/dev/null || echo "Нет конфигов"
```

Это поможет понять паттерн и настроить MasterConnect аналогично!

