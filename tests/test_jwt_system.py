import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/users"

def test_jwt_system():
    print("=== Тест системы JWT токенов ===\n")
    
    # 1. Регистрация пользователя
    print("1. Регистрация пользователя...")
    register_data = {
        "login": f"test_jwt_{int(time.time())}@example.com",
        "name": "JWT Test User",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✓ Пользователь создан: {user_data['login']}")
    else:
        print(f"✗ Ошибка регистрации: {response.text}")
        return
    
    # 2. Логин и получение токенов
    print("\n2. Логин и получение токенов...")
    login_data = {
        "login": register_data["login"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print("✓ Получены токены:")
        print(f"  - Access token: {tokens['access_token'][:50]}...")
        print(f"  - Refresh token: {tokens['refresh_token'][:50]}...")
        
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
    else:
        print(f"✗ Ошибка логина: {response.text}")
        return
    
    # 3. Тест доступа к защищенному эндпоинту
    print("\n3. Тест доступа к защищенному эндпоинту...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Доступ к защищенному эндпоинту получен")
    else:
        print(f"✗ Ошибка доступа: {response.text}")
    
    # 4. Тест обновления токенов
    print("\n4. Тест обновления токенов...")
    refresh_data = {"refresh_token": refresh_token}
    response = requests.post(f"{BASE_URL}/refresh", json=refresh_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        new_tokens = response.json()
        print("✓ Токены обновлены:")
        print(f"  - Новый access token: {new_tokens['access_token'][:50]}...")
        print(f"  - Новый refresh token: {new_tokens['refresh_token'][:50]}...")
        
        # Обновляем токены для следующего теста
        access_token = new_tokens['access_token']
    else:
        print(f"✗ Ошибка обновления токенов: {response.text}")
    
    # 5. Тест логаута
    print("\n5. Тест логаута...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Успешный логаут")
    else:
        print(f"✗ Ошибка логаута: {response.text}")
    
    # 6. Проверка, что токен инвалидирован
    print("\n6. Проверка инвалидации токена...")
    response = requests.get(f"{BASE_URL}/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Токен успешно инвалидирован")
    else:
        print("✗ Токен не был инвалидирован")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_jwt_system() 