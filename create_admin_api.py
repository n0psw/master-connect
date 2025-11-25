#!/usr/bin/env python3
"""
Скрипт для создания администратора через API.
"""
import requests
import json

def create_admin():
    """Создание администратора через API."""
    print("🔧 Создание администратора через API...")
    
    # Данные администратора
    admin_data = {
        "email": "admin@masterconnect.kz",
        "password": "admin123456",
        "name": "Администратор",
        "role": "admin",
        "phone": "+7 777 123 4567",
        "timezone": "UTC",
        "locale": "ru"
    }
    
    try:
        # Отправляем запрос на регистрацию
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("\n✅ Администратор успешно создан!")
            print(f"📧 Email: {admin_data['email']}")
            print(f"👤 Имя: {admin_data['name']}")
            print(f"🔑 Роль: admin")
            print(f"\n🌐 Теперь вы можете войти в систему:")
            print(f"   - API: http://localhost:8000/docs")
            print(f"   - Логин: POST /api/v1/auth/login")
            print(f"   - Email: {admin_data['email']}")
            print(f"   - Password: {admin_data['password']}")
            
            # Показываем токен
            if 'access_token' in result:
                print(f"\n🔑 Access Token: {result['access_token'][:50]}...")
                
        elif response.status_code == 409:
            print("⚠️ Администратор с таким email уже существует!")
            print("Попробуйте войти в систему с существующими данными:")
            print(f"   - Email: {admin_data['email']}")
            print(f"   - Password: {admin_data['password']}")
            
        else:
            print(f"❌ Ошибка при создании администратора:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к API серверу!")
        print("Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    create_admin()
