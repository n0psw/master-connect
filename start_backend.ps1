# Скрипт для запуска backend сервера MasterConnect

Write-Host "🚀 Запуск MasterConnect Backend..." -ForegroundColor Cyan

# Переходим в директорию backend
Set-Location -Path "$PSScriptRoot\apps\api"

Write-Host "📂 Рабочая директория: $(Get-Location)" -ForegroundColor Yellow
Write-Host "🗄️  База данных: $PSScriptRoot\apps\api\src\test.db" -ForegroundColor Yellow

# Проверяем наличие виртуального окружения
if (-not (Test-Path "$PSScriptRoot\venv\Scripts\python.exe")) {
    Write-Host "❌ Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "   Создайте его командой: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Проверяем наличие .env файла
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Файл .env не найден, копирую из test.env..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\test.env" ".env"
}

Write-Host "✅ Запуск сервера на http://localhost:8000" -ForegroundColor Green
Write-Host "📖 API документация: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# Запускаем backend
& "$PSScriptRoot\venv\Scripts\python.exe" "src\main.py"

