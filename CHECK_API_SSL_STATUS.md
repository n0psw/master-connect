# Проверка статуса SSL для API

Выполните эти команды для диагностики:

```bash
# 1. Проверьте, подключен ли API контейнер к сети proxy
docker network inspect proxy | grep -A 5 masterconnect_api

# 2. Проверьте переменные окружения API контейнера
docker inspect masterconnect_api | grep -A 10 VIRTUAL_HOST

# 3. Проверьте, видит ли nginx-proxy API контейнер
docker exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A 10 apiconnect

# 4. Проверьте логи nginx-proxy-acme подробнее
docker logs nginx-proxy-acme 2>&1 | grep -i apiconnect | tail -20

# 5. Проверьте, есть ли сертификаты для apiconnect
docker exec nginx-proxy ls -la /etc/nginx/certs/ | grep apiconnect

# 6. Проверьте DNS для apiconnect.mastereducation.kz
nslookup apiconnect.mastereducation.kz

# 7. Проверьте, работает ли API через HTTP
curl -I http://apiconnect.mastereducation.kz/api/v1/health
```

После выполнения этих команд пришлите вывод, чтобы понять, в чём проблема.

