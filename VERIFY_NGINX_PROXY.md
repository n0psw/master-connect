# Проверка подключения API к nginx-proxy

Контейнер подключен к сети proxy. Теперь проверьте:

```bash
# 1. Проверьте, что контейнер в сети proxy
docker network inspect proxy | grep -A 10 masterconnect_api

# 2. Проверьте переменные окружения VIRTUAL_HOST
docker inspect masterconnect_api | grep -A 10 VIRTUAL_HOST

# 3. Проверьте, видит ли nginx-proxy API контейнер (должен появиться конфиг)
docker exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A 15 apiconnect

# 4. Проверьте HTTP (должен работать, не 503)
curl -I http://apiconnect.mastereducation.kz/api/v1/health

# 5. Подождите 1-2 минуты и проверьте логи nginx-proxy-acme
sleep 60
docker logs nginx-proxy-acme --tail 50 | grep apiconnect

# 6. Проверьте HTTPS
curl -I https://apiconnect.mastereducation.kz/api/v1/health
```

Выполните команды и пришлите результаты команд 3, 4 и 6.

