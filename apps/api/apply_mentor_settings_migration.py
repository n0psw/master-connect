#!/usr/bin/env python3
"""
Скрипт для применения миграции mentor_settings.
"""
import asyncio
import sys
import os
from sqlalchemy import text

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings

async def apply_migration():
    """Применение миграции для создания таблицы mentor_settings."""
    print("Применение миграции mentor_settings...")
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        # Проверяем, существует ли таблица
        check_table = text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='mentor_settings'
        """)
        result = await conn.execute(check_table)
        table_exists = result.fetchone() is not None
        
        if table_exists:
            print("Таблица mentor_settings уже существует")
            return True
        
        # Создаем таблицу mentor_settings
        create_table = text("""
            CREATE TABLE mentor_settings (
                mentor_id CHAR(36) NOT NULL,
                timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
                buffer_time_minutes INTEGER NOT NULL DEFAULT 15,
                max_bookings_per_day INTEGER NOT NULL DEFAULT 8,
                advance_booking_days INTEGER NOT NULL DEFAULT 30,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (mentor_id),
                FOREIGN KEY(mentor_id) REFERENCES mentors (user_id) ON DELETE CASCADE
            )
        """)
        
        await conn.execute(create_table)
        print("Таблица mentor_settings создана")
        
        # Мигрируем существующие timezone из users в mentor_settings
        migrate_timezone = text("""
            INSERT INTO mentor_settings (mentor_id, timezone, buffer_time_minutes, max_bookings_per_day, advance_booking_days)
            SELECT m.user_id, u.timezone, 15, 8, 30
            FROM mentors m
            JOIN users u ON m.user_id = u.id
            WHERE NOT EXISTS (
                SELECT 1 FROM mentor_settings ms WHERE ms.mentor_id = m.user_id
            )
        """)
        
        result = await conn.execute(migrate_timezone)
        print(f"Мигрированы настройки для {result.rowcount} менторов")
        
        return True

async def main():
    """Главная функция."""
    try:
        success = await apply_migration()
        if success:
            print("\nМиграция успешно применена!")
            print("Таблица mentor_settings создана")
            print("Настройки менторов мигрированы")
            print("\nТеперь можно перезапустить API сервер и протестировать сохранение настроек!")
        else:
            print("\nОшибка применения миграции")
            sys.exit(1)
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())