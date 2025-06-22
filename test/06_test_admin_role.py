#!/usr/bin/env python3
"""
Тест 6: Функционал роли АДМИНИСТРАТОР
Тестирует полный функционал администратора с авторизацией:
- Управление пользователями (создание, просмотр, редактирование)
- Управление ролями
- Назначение ролей пользователям
- Аудит системы
- Доступ к аналитике
"""

import requests
import json
from typing import Dict, Any, Optional

# Конфигурация
AUTH_BASE_URL = "http://localhost:8001"
BACKEND_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Данные тестового администратора
ADMIN_CREDENTIALS = {
    "username": "test_admin",
    "password": "TestAdmin123!"
}

class AdminTester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.test_user_id: Optional[int] = None
    
    def authenticate(self) -> bool:
        """Авторизация администратора"""
        print("🔐 Авторизация администратора...")
        
        try:
            response = requests.post(
                f"{AUTH_BASE_URL}/auth/login",
                data={
                    "username": "test_admin",
                    "password": "TestAdmin123!"
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
                print("✅ Авторизация успешна")
                return True
            else:
                print(f"❌ Ошибка авторизации: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при авторизации: {e}")
            return False
    
    def test_get_users(self) -> bool:
        """Тест получения списка пользователей"""
        print("\n👥 Тест: Получение списка пользователей")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/users/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                users_data = response.json()
                users = users_data.get("users", []) if isinstance(users_data, dict) else users_data
                print(f"✅ Получен список пользователей: {len(users)} записей")
                
                # Подсчет по ролям
                roles_count = {}
                for user in users:
                    if isinstance(user, dict):
                        role = user.get("role", "unknown")
                        roles_count[role] = roles_count.get(role, 0) + 1
                
                print("   📊 Распределение по ролям:")
                for role, count in roles_count.items():
                    print(f"      {role}: {count}")
                
                return True
            else:
                print(f"❌ Ошибка получения пользователей: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении пользователей: {e}")
            return False
    
    def test_create_user(self) -> bool:
        """Тест создания нового пользователя"""
        print("\n👤 Тест: Создание нового пользователя")
        
        user_data = {
            "username": "admin_test_user",
            "email": "admin_test@example.com",
            "full_name": "Тестовый пользователь от админа",
            "role": "agent",
            "password": "TestPassword123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/users/",
                headers=self.headers,
                json=user_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                user = response.json()
                self.test_user_id = user.get("id")
                print(f"✅ Пользователь создан успешно (ID: {self.test_user_id})")
                return True
            else:
                print(f"❌ Ошибка создания пользователя: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при создании пользователя: {e}")
            return False
    
    def get_real_user_id(self) -> int:
        """Получение реального ID пользователя из списка"""
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/users/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                users_data = response.json()
                users = users_data.get("users", []) if isinstance(users_data, dict) else users_data
                
                # Ищем любого пользователя кроме админа для тестов
                for user in users:
                    if isinstance(user, dict) and user.get("role") != "admin":
                        return user.get("id")
                        
                # Если не нашли, возвращаем первого пользователя
                if users and len(users) > 0:
                    return users[0].get("id", 1)
                    
            return 1  # Fallback ID
        except:
            return 1  # Fallback ID
    
    def test_get_roles(self) -> bool:
        """Тест получения списка ролей"""
        print("\n🔑 Тест: Получение списка ролей")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/users/admin/roles",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                roles_data = response.json()
                print("✅ Список ролей получен")
                
                if isinstance(roles_data, dict) and "roles" in roles_data:
                    roles = roles_data["roles"]
                    # Извлекаем названия ролей из словарей
                    role_names = [role.get("role", "unknown") for role in roles]
                    print(f"   📋 Доступные роли: {', '.join(role_names)}")
                
                return True
            else:
                print(f"❌ Ошибка получения ролей: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении ролей: {e}")
            return False
    
    def test_assign_role(self) -> bool:
        """Тест назначения роли пользователю"""
        if not self.test_user_id:
            print("⚠️ Пропуск теста: пользователь не создан")
            return False
            
        print(f"\n🔄 Тест: Назначение роли пользователю {self.test_user_id}")
        
        try:
            # Используем query параметры как ожидает API
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/users/admin/roles/assign",
                headers=self.headers,
                params={
                    "user_id": self.test_user_id,
                    "new_role": "operator",
                    "reason": "Тестовое назначение роли администратором"
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Роль назначена успешно: {result.get('message', 'Успех')}")
                return True
            else:
                print(f"❌ Ошибка назначения роли: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при назначении роли: {e}")
            return False
    
    def test_audit_logs(self) -> bool:
        """Тест получения аудит логов"""
        print("\n📋 Тест: Получение аудит логов")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/users/admin/audit",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                audit_data = response.json()
                print("✅ Аудит логи получены")
                
                if isinstance(audit_data, dict):
                    total_actions = audit_data.get("total_actions", 0)
                    recent_actions = audit_data.get("recent_actions", [])
                    
                    print(f"   📊 Всего действий в системе: {total_actions}")
                    print(f"   🕒 Последние действия: {len(recent_actions)}")
                
                return True
            else:
                print(f"❌ Ошибка получения аудит логов: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении аудит логов: {e}")
            return False
    
    def test_analytics_access(self) -> bool:
        """Тест доступа к аналитике"""
        print("\n📊 Тест: Доступ к аналитике")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/dashboard",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                dashboard_data = response.json()
                print("✅ Дашборд аналитики доступен")
                return True
            else:
                print(f"❌ Ошибка доступа к аналитике: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при доступе к аналитике: {e}")
            return False
    
    def test_finance_reports_access(self) -> bool:
        """Тест доступа к финансовым отчетам"""
        print("\n💰 Тест: Доступ к финансовым отчетам")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/reports/finance",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                finance_report = response.json()
                print("✅ Финансовые отчеты доступны")
                return True
            else:
                print(f"❌ Ошибка доступа к финансовым отчетам: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при доступе к финансовым отчетам: {e}")
            return False
    
    def test_activity_reports_access(self) -> bool:
        """Тест доступа к отчетам активности"""
        print("\n📈 Тест: Доступ к отчетам активности")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/reports/activity",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                activity_report = response.json()
                print("✅ Отчеты активности доступны")
                return True
            else:
                print(f"❌ Ошибка доступа к отчетам активности: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при доступе к отчетам активности: {e}")
            return False
    
    def test_user_management(self) -> bool:
        """Тест управления пользователем"""
        # Используем реальный ID пользователя
        real_user_id = self.get_real_user_id()
        print(f"\n🔧 Тест: Управление пользователем {real_user_id}")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/users/{real_user_id}",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Информация о пользователе получена: {user_info.get('username', 'unknown')}")
                return True
            else:
                print(f"❌ Ошибка получения информации о пользователе: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при управлении пользователем: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Запуск всех тестов администратора"""
        print("🚀 Тестирование функционала роли АДМИНИСТРАТОР")
        print("=" * 60)
        
        # Авторизация
        if not self.authenticate():
            print("❌ Тестирование прервано: ошибка авторизации")
            return False
        
        # Список тестов
        tests = [
            ("Получение списка пользователей", self.test_get_users),
            ("Создание пользователя", self.test_create_user),
            ("Получение списка ролей", self.test_get_roles),
            ("Назначение роли", self.test_assign_role),
            ("Получение аудит логов", self.test_audit_logs),
            ("Доступ к аналитике", self.test_analytics_access),
            ("Доступ к финансовым отчетам", self.test_finance_reports_access),
            ("Доступ к отчетам активности", self.test_activity_reports_access),
            ("Управление пользователями", self.test_user_management),
        ]
        
        # Выполнение тестов
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ Исключение в тесте '{test_name}': {e}")
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        success_rate = (passed / total) * 100
        print(f"📊 Результат тестирования АДМИНИСТРАТОРА: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 УСПЕХ! Функционал администратора работает корректно")
            return True
        else:
            print("⚠️ ВНИМАНИЕ! Есть проблемы с функционалом администратора")
            return False

def main():
    """Главная функция"""
    tester = AdminTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main() 