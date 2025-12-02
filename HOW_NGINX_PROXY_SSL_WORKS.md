# Как работает автоматический SSL в nginx-proxy

## Что происходит автоматически:

### 1. **nginx-proxy** смотрит на переменные окружения контейнеров
```yaml
environment:
  - VIRTUAL_HOST=connect.mastereducation.kz  # Какой домен
  - VIRTUAL_PORT=80                          # На какой порт проксировать
  - LETSENCRYPT_HOST=connect.mastereducation.kz  # Для какого домена получить SSL
  - LETSENCRYPT_EMAIL=admin@mastereducation.kz   # Email для Let's Encrypt
```

### 2. **nginx-proxy-acme** (контейнер `nginx-proxy-acme`) видит эти переменные

Он постоянно:
- Слушает события Docker (через `docker.sock`)
- Видит новые контейнеры с `LETSENCRYPT_HOST`
- Автоматически получает SSL сертификат через Let's Encrypt
- Сохраняет сертификаты в `/opt/nginx-proxy/certs/`

### 3. **nginx-proxy** автоматически настраивает HTTPS

После получения сертификата nginx-proxy:
- Создаёт конфиг с HTTPS
- Настраивает редирект с HTTP на HTTPS
- Всё работает автоматически!

---

## Что уже есть на сервере:

```bash
# У тебя уже работает:
nginx-proxy              # Основной reverse proxy
nginx-proxy-acme         # Автоматическое получение SSL

# Уже есть SSL для других доменов:
- ielts.mastereducation.kz ✅
- auth.mastereducation.kz ✅
- api.ieltsdemo.mastereducation.kz ✅
```

**Все они получили SSL автоматически** через те же переменные! 🎉

---

## Что происходит когда перезапускаешь web:

1. **docker compose up -d web** → контейнер перезапускается
2. **nginx-proxy** видит переменные `VIRTUAL_HOST` → создаёт конфиг HTTP
3. **nginx-proxy-acme** видит `LETSENCRYPT_HOST` → начинает получать сертификат
4. **Через 2-5 минут:** сертификат получен
5. **nginx-proxy** автоматически настраивает HTTPS
6. **Готово!** ✅

---

## Можно проверить процесс:

```bash
# 1. Перезапусти web
docker compose up -d web

# 2. Смотри логи nginx-proxy-acme (там будет видно получение сертификата)
docker logs nginx-proxy-acme --tail -f

# 3. Через пару минут проверь, появился ли сертификат
docker exec -it nginx-proxy ls -la /etc/nginx/certs/ | grep connect

# 4. Проверь HTTPS
curl -I https://connect.mastereducation.kz
```

---

## Почему это работает:

- ✅ `nginx-proxy-acme` уже запущен и работает
- ✅ Он уже получил SSL для других доменов (ielts, auth, etc.)
- ✅ Тот же механизм сработает для `connect.mastereducation.kz`
- ✅ DNS уже указывает на этот сервер (проверили)
- ✅ Порты 80 и 443 открыты через nginx-proxy

**Ничего дополнительно настраивать не нужно!** Просто перезапусти контейнер. 🚀

