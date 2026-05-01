import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/users"

def test_authorization_logic():
    print("=== Тест новой логики авторизации ===\n")
    
    # 1. Создаем обычного пользователя
    print("1. Создание обычного пользователя...")
    user_data = {
        "login": f"user_test_{int(time.time())}@example.com",
        "name": "Test User",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    if response.status_code != 200:
        print(f"✗ Ошибка создания пользователя: {response.text}")
        return
    
    user_info = response.json()
    user_id = user_info['id']
    print(f"✓ Пользователь создан: {user_info['login']} (ID: {user_id})")
    
    # 2. Логинимся как обычный пользователь
    print("\n2. Логин обычного пользователя...")
    login_data = {
        "login": user_data["login"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code != 200:
        print(f"✗ Ошибка логина: {response.text}")
        return
    
    tokens = response.json()
    user_access_token = tokens['access_token']
    print("✓ Получен токен обычного пользователя")
    
    # 3. Тест: обычный пользователь получает свои данные
    print("\n3. Тест: обычный пользователь получает свои данные...")
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Обычный пользователь может получить свои данные")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # 4. Тест: обычный пользователь пытается получить данные другого пользователя
    print("\n4. Тест: обычный пользователь пытается получить данные другого пользователя...")
    other_user_id = user_id + 1  # Несуществующий ID
    response = requests.get(f"{BASE_URL}/{other_user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✓ Обычный пользователь не может получить данные другого пользователя")
    else:
        print(f"✗ Неожиданный результат: {response.text}")
    
    # 5. Создаем админа (вручную в БД или через seeder)
    print("\n5. Создание админа...")
    admin_data = {
        "login": f"admin_test_{int(time.time())}@example.com",
        "name": "Test Admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=admin_data)
    if response.status_code != 200:
        print(f"✗ Ошибка создания админа: {response.text}")
        return
    
    admin_info = response.json()
    admin_id = admin_info['id']
    print(f"✓ Админ создан: {admin_info['login']} (ID: {admin_id})")
    
    # 6. Логинимся как админ
    print("\n6. Логин админа...")
    admin_login_data = {
        "login": admin_data["login"],
        "password": admin_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/login", json=admin_login_data)
    if response.status_code != 200:
        print(f"✗ Ошибка логина админа: {response.text}")
        return
    
    admin_tokens = response.json()
    admin_access_token = admin_tokens['access_token']
    print("✓ Получен токен админа")
    
    # 7. Тест: админ получает данные обычного пользователя
    print("\n7. Тест: админ получает данные обычного пользователя...")
    admin_headers = {"Authorization": f"Bearer {admin_access_token}"}
    response = requests.get(f"{BASE_URL}/{user_id}", headers=admin_headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Админ может получить данные обычного пользователя")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # 8. Тест: админ получает свои данные
    print("\n8. Тест: админ получает свои данные...")
    response = requests.get(f"{BASE_URL}/{admin_id}", headers=admin_headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Админ может получить свои данные")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # 9. Тест: обычный пользователь пытается удалить другого пользователя
    print("\n9. Тест: обычный пользователь пытается удалить другого пользователя...")
    response = requests.delete(f"{BASE_URL}/{other_user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✓ Обычный пользователь не может удалить другого пользователя")
    else:
        print(f"✗ Неожиданный результат: {response.text}")
    
    # 10. Тест: обычный пользователь удаляет себя
    print("\n10. Тест: обычный пользователь удаляет себя...")
    response = requests.delete(f"{BASE_URL}/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Обычный пользователь может удалить себя")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_authorization_logic() 