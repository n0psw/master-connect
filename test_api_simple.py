#!/usr/bin/env python3
"""
Простой тест для проверки API endpoints.
"""
import requests
import time

def test_api():
    """Тестирование API endpoints."""
    base_url = "http://localhost:8000"
    
    print("Тестирование API endpoints...")
    
    # Ждем запуска сервера
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("API сервер запущен")
                break
        except requests.exceptions.RequestException:
            print(f"Ожидание запуска сервера... ({i+1}/5)")
            time.sleep(2)
    else:
        print("API сервер не запустился")
        return False
    
    # Проверяем availability endpoints
    try:
        response = requests.get(f"{base_url}/availability/health", timeout=5)
        if response.status_code == 200:
            print("Availability module работает")
        else:
            print(f"Availability module ошибка: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка availability module: {e}")
    
    # Проверяем docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("API документация доступна")
        else:
            print(f"API документация недоступна: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка API документации: {e}")
    
    return True

if __name__ == "__main__":
    test_api()
