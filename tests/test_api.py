import requests
import json
import time

# Тест основного эндпоинта
print("=== Тест основного эндпоинта ===")
response = requests.get('http://127.0.0.1:8000/')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Тест регистрации пользователя
print("\n=== Тест регистрации пользователя ===")
timestamp = int(time.time())
data = {
    'login': f'test{timestamp}@example.com',
    'name': 'Test User',
    'password': 'password123'
}
response = requests.post('http://127.0.0.1:8000/api/v1/users/register', json=data)
print(f"Status: {response.status_code}")
print(f"Response text: {response.text}")
try:
    print(f"Response JSON: {response.json()}")
except:
    print("Response is not JSON")

# Тест логина с новым пользователем
print("\n=== Тест логина с новым пользователем ===")
login_data = {
    'login': f'test{timestamp}@example.com',
    'password': 'password123'
}
response = requests.post('http://127.0.0.1:8000/api/v1/users/login', json=login_data)
print(f"Status: {response.status_code}")
print(f"Response text: {response.text}")
try:
    print(f"Response JSON: {response.json()}")
except:
    print("Response is not JSON") 