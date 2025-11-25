#!/usr/bin/env python3
"""
Скрипт для добавления timestamp полей в таблицу mentor_settings.
"""
import asyncio
import sys
import os
from sqlalchemy import text

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings

async def add_timestamps_to_mentor_settings():
    """Добавление timestamp полей в таблицу mentor_settings."""
    print("Добавление timestamp полей в mentor_settings...")
    
    # Создаем подключение к БД
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        # Проверяем, существуют ли поля
        check_columns = text("""
            PRAGMA table_info(mentor_settings)
        """)
        result = await conn.execute(check_columns)
        columns = result.fetchall()
        
        column_names = [col[1] for col in columns]
        
        if 'created_at' in column_names and 'updated_at' in column_names:
            print("Timestamp поля уже существуют")
            return True
        
        # Добавляем поля created_at и updated_at
        if 'created_at' not in column_names:
            add_created_at = text("""
                ALTER TABLE mentor_settings 
                ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            """)
            await conn.execute(add_created_at)
            print("Добавлено поле created_at")
        
        if 'updated_at' not in column_names:
            add_updated_at = text("""
                ALTER TABLE mentor_settings 
                ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
            """)
            await conn.execute(add_updated_at)
            print("Добавлено поле updated_at")
        
        # Обновляем существующие записи, устанавливая текущее время
        update_timestamps = text("""
            UPDATE mentor_settings 
            SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL OR updated_at IS NULL
        """)
        result = await conn.execute(update_timestamps)
        print(f"Обновлено {result.rowcount} записей")
        
        return True

async def main():
    """Главная функция."""
    try:
        success = await add_timestamps_to_mentor_settings()
        if success:
            print("\nМиграция успешно применена!")
            print("Timestamp поля добавлены в таблицу mentor_settings")
            print("\nТеперь можно перезапустить API сервер!")
        else:
            print("\nОшибка применения миграции")
            sys.exit(1)
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
