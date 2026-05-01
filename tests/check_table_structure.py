import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

print("=== Проверка структуры таблицы users ===")

try:
    db = SessionLocal()
    
    # Получаем структуру таблицы users
    result = db.execute(text("DESCRIBE users"))
    columns = result.fetchall()
    
    print("Структура таблицы users:")
    for column in columns:
        print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
        
    db.close()
    
except Exception as e:
    print(f"✗ Ошибка: {e}") 