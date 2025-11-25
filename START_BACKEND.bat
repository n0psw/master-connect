@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   ЗАПУСК MASTERCONNECT BACKEND
echo ========================================
echo.

cd /d "%~dp0apps\api"

echo [+] Рабочая директория: %CD%
echo [+] База данных: %CD%\src\test.db
echo.
echo [+] Запуск сервера на http://localhost:8000
echo [+] Нажмите CTRL+C для остановки
echo.

"%~dp0venv\Scripts\python.exe" src\main.py

