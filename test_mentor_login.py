#!/usr/bin/env python3
"""
Тестовый скрипт для проверки логина ментора
"""
import requests
import json

# Тестируем логин ментора
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "mentor@test.com",
        "password": "password123"
    }
)

print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Проверяем роль
if response.status_code == 200:
    data = response.json()
    role = data.get("user", {}).get("role")
    print(f"\n✅ Роль пользователя: {role}")
    print(f"   Тип: {type(role)}")




