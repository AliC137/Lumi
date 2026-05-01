#!/usr/bin/env python3
"""
Интеграционный тест для проверки всей системы контекстного управления.
"""

import sys
import os
import requests
import json
from typing import Dict, Any

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Конфигурация теста
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Тестовые данные
TEST_ADMIN = {
    "login": "admin1@example.com",
    "password": "admin123"
}

TEST_USER = {
    "login": "user1@example.com", 
    "password": "password1"
}


class IntegrationTester:
    """Класс для интеграционного тестирования."""
    
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_data = {}
    
    def test_server_connection(self):
        """Тестирует подключение к серверу."""
        print("🔍 Testing server connection...")
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Server is running")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
            return False
    
    def test_admin_login(self):
        """Тестирует вход администратора."""
        print("\n🔍 Testing admin login...")
        try:
            response = requests.post(f"{API_BASE}/users/login", json=TEST_ADMIN)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                print("✅ Admin login successful")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            return False
    
    def test_user_login(self):
        """Тестирует вход обычного пользователя."""
        print("\n🔍 Testing user login...")
        try:
            response = requests.post(f"{API_BASE}/users/login", json=TEST_USER)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("access_token")
                print("✅ User login successful")
                return True
            else:
                print(f"❌ User login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User login error: {e}")
            return False
    
    def test_subject_types_api(self):
        """Тестирует API типов субъектов."""
        print("\n🔍 Testing subject types API...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Получаем все типы субъектов
            response = requests.get(f"{API_BASE}/subject-types/", headers=headers)
            if response.status_code == 200:
                subject_types = response.json()
                print(f"✅ Found {len(subject_types)} subject types")
                
                # Сохраняем первый тип для дальнейших тестов
                if subject_types:
                    self.test_data["subject_type_id"] = subject_types[0]["id"]
                    self.test_data["subject_type_slug"] = subject_types[0]["slug"]
                
                return True
            else:
                print(f"❌ Failed to get subject types: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Subject types API error: {e}")
            return False
    
    def test_roles_api(self):
        """Тестирует API ролей."""
        print("\n🔍 Testing roles API...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Получаем все роли
            response = requests.get(f"{API_BASE}/roles/", headers=headers)
            if response.status_code == 200:
                roles = response.json()
                print(f"✅ Found {len(roles)} roles")
                
                # Сохраняем роль owner для дальнейших тестов
                owner_role = next((r for r in roles if r["slug"] == "owner"), None)
                if owner_role:
                    self.test_data["owner_role_id"] = owner_role["id"]
                
                return True
            else:
                print(f"❌ Failed to get roles: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Roles API error: {e}")
            return False
    
    def test_subjects_api(self):
        """Тестирует API субъектов."""
        print("\n🔍 Testing subjects API...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Получаем все субъекты
            response = requests.get(f"{API_BASE}/subjects/", headers=headers)
            if response.status_code == 200:
                subjects = response.json()
                print(f"✅ Found {len(subjects)} subjects")
                
                # Сохраняем первый субъект для дальнейших тестов
                if subjects:
                    self.test_data["subject_id"] = subjects[0]["id"]
                
                return True
            else:
                print(f"❌ Failed to get subjects: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Subjects API error: {e}")
            return False
    
    def test_user_subjects_api(self):
        """Тестирует API связей пользователь-субъект."""
        print("\n🔍 Testing user subjects API...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Получаем все связи
            response = requests.get(f"{API_BASE}/user-subjects/", headers=headers)
            if response.status_code == 200:
                connections = response.json()
                print(f"✅ Found {len(connections)} user-subject connections")
                return True
            else:
                print(f"❌ Failed to get user subjects: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User subjects API error: {e}")
            return False
    
    def test_hierarchical_operations(self):
        """Тестирует иерархические операции."""
        print("\n🔍 Testing hierarchical operations...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Получаем корневые субъекты
            response = requests.get(f"{API_BASE}/subjects/root/all", headers=headers)
            if response.status_code == 200:
                root_subjects = response.json()
                print(f"✅ Found {len(root_subjects)} root subjects")
                
                # Тестируем иерархию для первого субъекта
                if root_subjects:
                    subject_id = root_subjects[0]["id"]
                    
                    # Получаем иерархию
                    hierarchy_response = requests.get(
                        f"{API_BASE}/subjects/{subject_id}/hierarchy", 
                        headers=headers
                    )
                    if hierarchy_response.status_code == 200:
                        hierarchy = hierarchy_response.json()
                        print(f"✅ Subject hierarchy has {len(hierarchy)} levels")
                    
                    # Получаем количество дочерних элементов
                    children_response = requests.get(
                        f"{API_BASE}/subjects/{subject_id}/children-count", 
                        headers=headers
                    )
                    if children_response.status_code == 200:
                        children_count = children_response.json()
                        print(f"✅ Subject has {children_count['children_count']} children")
                
                return True
            else:
                print(f"❌ Failed to get root subjects: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Hierarchical operations error: {e}")
            return False
    
    def test_authorization(self):
        """Тестирует авторизацию."""
        print("\n🔍 Testing authorization...")
        
        if not self.user_token:
            print("❌ No user token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Пытаемся получить все субъекты с токеном обычного пользователя
            response = requests.get(f"{API_BASE}/subjects/", headers=headers)
            if response.status_code == 403:
                print("✅ Authorization working correctly - user cannot access admin endpoints")
                return True
            else:
                print(f"❌ Authorization failed - user got access: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authorization test error: {e}")
            return False
    
    def test_swagger_documentation(self):
        """Тестирует доступность Swagger документации."""
        print("\n🔍 Testing Swagger documentation...")
        
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("✅ Swagger documentation is accessible")
                return True
            else:
                print(f"❌ Swagger documentation not accessible: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Swagger documentation error: {e}")
            return False
    
    def run_all_tests(self):
        """Запускает все тесты."""
        print("🚀 Starting integration tests...\n")
        
        tests = [
            ("Server Connection", self.test_server_connection),
            ("Admin Login", self.test_admin_login),
            ("User Login", self.test_user_login),
            ("Subject Types API", self.test_subject_types_api),
            ("Roles API", self.test_roles_api),
            ("Subjects API", self.test_subjects_api),
            ("User Subjects API", self.test_user_subjects_api),
            ("Hierarchical Operations", self.test_hierarchical_operations),
            ("Authorization", self.test_authorization),
            ("Swagger Documentation", self.test_swagger_documentation),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Выводим итоговые результаты
        print("\n" + "="*50)
        print("📊 INTEGRATION TEST RESULTS")
        print("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print("="*50)
        print(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ ЭТАП 6: Тестирование и финализация - ЗАВЕРШЕН!")
            return True
        else:
            print(f"\n⚠️ {total - passed} test(s) failed")
            return False


def main():
    """Основная функция."""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 System is ready for production!")
        print("\n📋 Next steps:")
        print("1. Run migrations: poetry run alembic upgrade head")
        print("2. Seed test data: python aistudio/seeders/context_seeder.py")
        print("3. Start server: poetry run uvicorn aistudio.main:app --reload")
        print("4. Access Swagger UI: http://127.0.0.1:8000/docs")
    else:
        print("\n🔧 Please fix the failing tests before proceeding.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 