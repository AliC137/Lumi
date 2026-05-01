import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

print("=== Проверка структуры таблицы jwt_tokens ===")

try:
    db = SessionLocal()
    
    # Получаем структуру таблицы jwt_tokens
    result = db.execute(text("DESCRIBE jwt_tokens"))
    columns = result.fetchall()
    
    print("Структура таблицы jwt_tokens:")
    for column in columns:
        print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
        
    # Проверяем количество записей
    result = db.execute(text("SELECT COUNT(*) FROM jwt_tokens"))
    count = result.fetchone()[0]
    print(f"\nКоличество записей в jwt_tokens: {count}")
        
    db.close()
    
except Exception as e:
    print(f"✗ Ошибка: {e}") 