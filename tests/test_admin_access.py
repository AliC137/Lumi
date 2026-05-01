import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/users"

def test_admin_access():
    print("=== Тест доступа админа ===\n")
    
    # Логинимся как админ
    print("1. Логин админа...")
    admin_login_data = {
        "login": "admin_test_1753780122@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=admin_login_data)
    if response.status_code != 200:
        print(f"✗ Ошибка логина админа: {response.text}")
        return
    
    admin_tokens = response.json()
    admin_access_token = admin_tokens['access_token']
    print("✓ Получен токен админа")
    
    # Тест: админ получает данные обычного пользователя
    print("\n2. Тест: админ получает данные обычного пользователя...")
    admin_headers = {"Authorization": f"Bearer {admin_access_token}"}
    response = requests.get(f"{BASE_URL}/18", headers=admin_headers)  # ID обычного пользователя
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Админ может получить данные обычного пользователя")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # Тест: админ получает свои данные
    print("\n3. Тест: админ получает свои данные...")
    response = requests.get(f"{BASE_URL}/19", headers=admin_headers)  # ID админа
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Админ может получить свои данные")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # Тест: админ удаляет обычного пользователя
    print("\n4. Тест: админ удаляет обычного пользователя...")
    response = requests.delete(f"{BASE_URL}/18", headers=admin_headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Админ может удалить обычного пользователя")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_admin_access() 