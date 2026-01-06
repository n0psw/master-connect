# Проверка правильного пути для health endpoint

Проверьте на сервере:

```bash
# 1. Проверьте, работает ли /health без префикса
curl http://127.0.0.1:8000/health

# 2. Проверьте, работает ли /api/v1/health
curl http://127.0.0.1:8000/api/v1/health

# 3. Проверьте через nginx-proxy без префикса
curl -I http://apiconnect.mastereducation.kz/health

# 4. Проверьте, как nginx-proxy проксирует (может быть проблема с путем)
docker exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A 20 apiconnect
```

Возможная проблема: nginx-proxy проксирует на `http://masterconnect_api:8000`, но путь `/api/v1/health` может проксироваться неправильно. Нужно проверить конфигурацию nginx-proxy.




