import os
from dotenv import load_dotenv
from aistudio.services.user_service import UserService
from aistudio.schemas.user_create import UserCreate

# Загружаем переменные окружения
load_dotenv()

print("=== Тест сервиса пользователей ===")

try:
    service = UserService()
    
    # Создаем тестовые данные
    user_data = UserCreate(
        login="test_service@example.com",
        name="Test Service User",
        password="password123"
    )
    
    print("Попытка регистрации пользователя...")
    user = service.register_user(user_data)
    print(f"✓ Пользователь создан: {user.login}")
    
    print("Попытка аутентификации...")
    auth_user = service.authenticate_user("test_service@example.com", "password123")
    if auth_user:
        print(f"✓ Аутентификация успешна: {auth_user.login}")
    else:
        print("✗ Аутентификация не удалась")
        
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc() 