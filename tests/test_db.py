import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal, engine
from aistudio.models.user import User
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

print("=== Тест подключения к базе данных ===")
print(f"DB_HOST: {os.getenv('DB_HOST', 'не установлен')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'не установлен')}")
print(f"DB_USER: {os.getenv('DB_USER', 'не установлен')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'не установлен')}")

try:
    # Проверяем подключение к БД
    db = SessionLocal()
    print("✓ Подключение к БД успешно")
    
    # Проверяем существование таблицы users
    result = db.execute(text("SHOW TABLES LIKE 'users'"))
    tables = result.fetchall()
    if tables:
        print("✓ Таблица 'users' существует")
        
        # Проверяем количество пользователей
        users_count = db.query(User).count()
        print(f"✓ Количество пользователей в БД: {users_count}")
    else:
        print("✗ Таблица 'users' не существует")
        
    db.close()
    
except Exception as e:
    print(f"✗ Ошибка подключения к БД: {e}") 