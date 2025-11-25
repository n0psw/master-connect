#!/bin/bash

# Скрипт для тестирования основных API эндпоинтов
# Использование: ./test_api_endpoints.sh [API_URL]
# Пример: ./test_api_endpoints.sh http://localhost:8000

API_URL="${1:-http://localhost:8000}"
API_BASE="${API_URL}/api/v1"

echo "🧪 Тестирование API эндпоинтов MasterConnect"
echo "API URL: $API_BASE"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки эндпоинта
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    echo -n "Testing $method $endpoint ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}${endpoint}")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_BASE}${endpoint}")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ OK (${http_code})${NC}"
        return 0
    elif [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
        echo -e "${YELLOW}⚠️  Auth required (${http_code})${NC}"
        return 0
    elif [ "$http_code" -eq 404 ]; then
        echo -e "${YELLOW}⚠️  Not found (${http_code})${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (${http_code})${NC}"
        echo "   Response: $body"
        return 1
    fi
}

# Публичные эндпоинты
echo "=== Публичные эндпоинты ==="
test_endpoint "GET" "/health" "Health check"
test_endpoint "GET" "/mentors" "List mentors"
test_endpoint "GET" "/mentors/stats/overview" "Mentors stats"

echo ""
echo "=== Эндпоинты, требующие авторизации ==="
echo "(Эти эндпоинты должны вернуть 401 без токена)"
test_endpoint "GET" "/users/me" "Get my profile"
test_endpoint "GET" "/bookings/my" "Get my bookings"
test_endpoint "GET" "/availability/my/profile" "Get my availability"
test_endpoint "GET" "/admin/dashboard" "Admin dashboard"

echo ""
echo "=== Проверка CORS ==="
cors_response=$(curl -s -I -X OPTIONS "${API_BASE}/health" \
    -H "Origin: http://connect.mastereducation.kz" \
    -H "Access-Control-Request-Method: GET")

if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✅ CORS headers present${NC}"
else
    echo -e "${RED}❌ CORS headers missing${NC}"
fi

echo ""
echo "✅ Тестирование завершено!"
echo ""
echo "Для полного тестирования с авторизацией используйте:"
echo "  export TOKEN='your_access_token'"
echo "  curl -H \"Authorization: Bearer \$TOKEN\" ${API_BASE}/users/me"

