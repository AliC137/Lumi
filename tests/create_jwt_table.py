import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

print("=== Создание таблицы jwt_tokens ===")

try:
    db = SessionLocal()
    
    # Создаем таблицу jwt_tokens
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS jwt_tokens (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        access_token VARCHAR(1000) NOT NULL,
        refresh_token VARCHAR(1000) NOT NULL,
        access_token_expired_time DATETIME NOT NULL,
        refresh_token_expired_time DATETIME NOT NULL,
        created_dt DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_dt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
        deleted_dt DATETIME NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
    
    db.execute(text(create_table_sql))
    db.commit()
    
    print("✓ Таблица jwt_tokens создана успешно")
    
    # Проверяем структуру
    result = db.execute(text("DESCRIBE jwt_tokens"))
    columns = result.fetchall()
    
    print("\nСтруктура таблицы jwt_tokens:")
    for column in columns:
        print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
        
    db.close()
    
except Exception as e:
    print(f"✗ Ошибка: {e}") 