#!/usr/bin/env python3
"""
Скрипт для отладки пользователей в базе данных.
"""
import sqlite3
import sys
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.security import verify_password

def debug_users():
    """Отладка пользователей в базе данных."""
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    print('=== DEBUG: Проверка пользователей ===')
    print()
    
    # Проверяем всех пользователей
    cursor.execute('SELECT id, email, password_hash, role, is_active, name FROM users')
    users = cursor.fetchall()
    
    print(f'Всего пользователей в базе: {len(users)}')
    print()
    
    test_accounts = [
        ("admin@test.com", "password123"),
        ("mentor@test.com", "password123"),
        ("student@test.com", "password123")
    ]
    
    for user_id, email, password_hash, role, is_active, name in users:
        print(f'User: {email}')
        print(f'  ID: {user_id}')
        print(f'  Role: {role}')
        print(f'  Active: {is_active}')
        print(f'  Name: {name}')
        print(f'  Password Hash: {password_hash[:50]}...')
        
        # Проверяем пароли для тестовых аккаунтов
        for test_email, test_password in test_accounts:
            if email == test_email:
                password_valid = verify_password(test_password, password_hash)
                print(f'  Password "{test_password}" valid: {password_valid}')
                if not password_valid:
                    print(f'  *** PASSWORD MISMATCH FOR {email} ***')
        print()
    
    conn.close()

if __name__ == "__main__":
    debug_users()








