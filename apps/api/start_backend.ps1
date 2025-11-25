# Установка переменных окружения
$env:SECRET_KEY="your-secret-key-here"
$env:JWT_SECRET_KEY="your-jwt-secret-key"
$env:APP_ENV="development"
$env:DEBUG="true"
$env:BACKEND_CORS_ORIGINS='["http://localhost:3000","http://localhost:5173","http://localhost:8080"]'
$env:REDIS_URL="redis://localhost:6379/0"
$env:S3_BUCKET="dummy"
$env:S3_ACCESS_KEY="dummy"
$env:S3_SECRET_KEY="dummy"
$env:S3_REGION="us-east-1"
$env:EMAIL_SMTP_HOST="smtp.gmail.com"
$env:EMAIL_SMTP_USER="dummy@example.com"
$env:EMAIL_SMTP_PASSWORD="dummy"
$env:EMAIL_FROM="dummy@example.com"
$env:GOOGLE_SERVICE_ACCOUNT_JSON_B64="dummy"
$env:GOOGLE_CALENDAR_ID="dummy"
$env:KASPI_PAYMENT_URL="dummy"
$env:RATE_LIMIT_WINDOW="60"
$env:MAX_FILE_SIZE_MB="10"
$env:ALLOWED_FILE_TYPES="pdf,jpg,jpeg,png,docx"
$env:BOOKING_HOLD_DURATION_MINUTES="10"

# Запуск сервера
Write-Host "🚀 Запуск backend сервера..."
python run_server.py







