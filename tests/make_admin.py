import os
from dotenv import load_dotenv
from aistudio.core.database import SessionLocal
from sqlalchemy import text

# Загружаем переменные окружения
load_dotenv()

def make_user_admin(email: str):
    """
    Изменяет роль пользователя на admin.
    """
    print(f"=== Изменение роли пользователя {email} на admin ===")
    
    try:
        db = SessionLocal()
        
        # Обновляем роль пользователя
        result = db.execute(
            text("UPDATE users SET role = 'admin' WHERE login = :email"),
            {"email": email}
        )
        db.commit()
        
        if result.rowcount > 0:
            print(f"✓ Роль пользователя {email} изменена на admin")
        else:
            print(f"✗ Пользователь {email} не найден")
            
        db.close()
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")

if __name__ == "__main__":
    # Изменяем роль админа из теста
    make_user_admin("admin_test_1753780122@example.com") 