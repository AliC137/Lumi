import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

print("=== Проверка состояния миграций ===")

try:
    db = SessionLocal()
    
    # Проверяем таблицу alembic_version
    result = db.execute(text("SHOW TABLES LIKE 'alembic_version'"))
    tables = result.fetchall()
    
    if tables:
        print("✓ Таблица alembic_version существует")
        
        # Проверяем текущую версию
        result = db.execute(text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()
        if version:
            print(f"✓ Текущая версия в БД: {version[0]}")
        else:
            print("✗ Версия не найдена в таблице alembic_version")
    else:
        print("✗ Таблица alembic_version не существует")
        
    db.close()
    
except Exception as e:
    print(f"✗ Ошибка: {e}") 