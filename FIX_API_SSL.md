# Исправление подключения API к сети proxy

## Проблема
API контейнер не подключен к сети `proxy`, поэтому nginx-proxy его не видит и не получает SSL сертификат.

## Решение

Выполните на сервере:

```bash
# 1. Остановите и удалите API контейнер
docker compose stop api
docker compose rm -f api

# 2. Запустите API контейнер заново (подключится к сети proxy)
docker compose up -d api

# 3. Проверьте, что API контейнер теперь в сети proxy
docker network inspect proxy | grep masterconnect_api

# 4. Проверьте логи nginx-proxy - должен появиться новый контейнер
docker logs nginx-proxy --tail 20

# 5. Подождите 1-2 минуты и проверьте логи nginx-proxy-acme
sleep 60
docker logs nginx-proxy-acme --tail 50 | grep apiconnect

# 6. Проверьте SSL
curl -I https://apiconnect.mastereducation.kz/api/v1/health
```

Если после этого SSL все еще не работает, проверьте DNS:
```bash
nslookup apiconnect.mastereducation.kz
```

DNS должен указывать на IP сервера (185.129.48.238).

