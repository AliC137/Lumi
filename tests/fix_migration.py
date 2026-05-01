import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

print("=== Исправление версии миграции ===")

try:
    db = SessionLocal()
    
    # Обновляем версию в таблице alembic_version
    db.execute(text("UPDATE alembic_version SET version_num = '5a36b2f48c9c'"))
    db.commit()
    
    # Проверяем результат
    result = db.execute(text("SELECT version_num FROM alembic_version"))
    version = result.fetchone()
    if version:
        print(f"✓ Версия обновлена: {version[0]}")
    else:
        print("✗ Версия не найдена")
        
    db.close()
    
except Exception as e:
    print(f"✗ Ошибка: {e}") 