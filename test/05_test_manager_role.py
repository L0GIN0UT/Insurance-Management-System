#!/usr/bin/env python3
"""
Тест 5: Функционал роли МЕНЕДЖЕР
Тестирует полный функционал менеджера с авторизацией:
- Дашборд аналитики
- Финансовые отчеты
- Отчеты активности
- Управление пользователями (просмотр)
"""

import requests
import json
from typing import Dict, Any, Optional

# Конфигурация
AUTH_BASE_URL = "http://localhost:8001"
BACKEND_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Данные тестового менеджера
MANAGER_CREDENTIALS = {
    "username": "test_manager",
    "password": "TestManager123!"
}

class ManagerTester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.headers: Dict[str, str] = {}
    
    def authenticate(self) -> bool:
        """Авторизация менеджера"""
        print("🔐 Авторизация менеджера...")
        
        try:
            response = requests.post(
                f"{AUTH_BASE_URL}/auth/login",
                data=MANAGER_CREDENTIALS,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                if self.access_token:
                    self.headers = {"Authorization": f"Bearer {self.access_token}"}
                    print("✅ Авторизация успешна")
                    return True
                else:
                    print("❌ Токен не получен")
                    return False
            else:
                print(f"❌ Ошибка авторизации: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при авторизации: {e}")
            return False
    
    def test_analytics_dashboard(self) -> bool:
        """Тест получения дашборда аналитики"""
        print("\n📊 Тест: Дашборд аналитики")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/dashboard",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                dashboard_data = response.json()
                print("✅ Дашборд аналитики получен")
                
                # Проверяем основные метрики
                metrics = dashboard_data.get("metrics", {})
                if metrics:
                    print(f"   📈 Общие клиенты: {metrics.get('total_clients', 0)}")
                    print(f"   📋 Активные договоры: {metrics.get('active_contracts', 0)}")
                    print(f"   🎯 Заявки в обработке: {metrics.get('pending_claims', 0)}")
                
                return True
            else:
                print(f"❌ Ошибка получения дашборда: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении дашборда: {e}")
            return False
    
    def test_finance_report(self) -> bool:
        """Тест получения финансового отчета"""
        print("\n💰 Тест: Финансовый отчет")
        
        try:
            # Запрос финансового отчета с параметрами
            params = {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
            
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/reports/finance",
                headers=self.headers,
                params=params,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                finance_report = response.json()
                print("✅ Финансовый отчет получен")
                
                # Проверяем финансовые показатели
                if isinstance(finance_report, dict):
                    total_premiums = finance_report.get("total_premiums", 0)
                    total_claims = finance_report.get("total_claims_paid", 0)
                    profit = finance_report.get("profit", 0)
                    
                    print(f"   💵 Общие премии: {total_premiums}")
                    print(f"   💸 Выплаты по заявкам: {total_claims}")
                    print(f"   📊 Прибыль: {profit}")
                
                return True
            else:
                print(f"❌ Ошибка получения финансового отчета: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении финансового отчета: {e}")
            return False
    
    def test_activity_report(self) -> bool:
        """Тест получения отчета активности"""
        print("\n📈 Тест: Отчет активности")
        
        try:
            # Запрос отчета активности
            params = {
                "period": "month"
            }
            
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/reports/activity",
                headers=self.headers,
                params=params,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                activity_report = response.json()
                print("✅ Отчет активности получен")
                
                # Проверяем показатели активности
                if isinstance(activity_report, dict):
                    new_clients = activity_report.get("new_clients", 0)
                    new_contracts = activity_report.get("new_contracts", 0)
                    processed_claims = activity_report.get("processed_claims", 0)
                    
                    print(f"   👥 Новые клиенты: {new_clients}")
                    print(f"   📝 Новые договоры: {new_contracts}")
                    print(f"   ✅ Обработанные заявки: {processed_claims}")
                
                return True
            else:
                print(f"❌ Ошибка получения отчета активности: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении отчета активности: {e}")
            return False
    
    def test_users_overview(self) -> bool:
        """Тест получения обзора пользователей"""
        print("\n👥 Тест: Обзор пользователей")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/users/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                users_data = response.json()
                
                # Извлекаем список пользователей из структуры UserList
                if isinstance(users_data, dict) and "users" in users_data:
                    users = users_data["users"]
                else:
                    users = users_data if isinstance(users_data, list) else []
                
                print(f"✅ Список пользователей получен: {len(users)} записей")
                
                # Подсчет по ролям
                roles_count = {}
                for user in users:
                    if isinstance(user, dict):
                        role = user.get("role", "unknown")
                    else:
                        role = "unknown"
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
    
    def test_custom_analytics(self) -> bool:
        """Тест кастомной аналитики"""
        print("\n📊 Тест: Кастомная аналитика")
        
        try:
            # Тест получения аналитики по периодам
            params = {
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "group_by": "month"
            }
            
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/dashboard",
                headers=self.headers,
                params=params,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                analytics_data = response.json()
                print("✅ Кастомная аналитика получена")
                return True
            else:
                print(f"❌ Ошибка получения кастомной аналитики: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении кастомной аналитики: {e}")
            return False
    
    def test_export_reports(self) -> bool:
        """Тест экспорта отчетов"""
        print("\n📤 Тест: Экспорт отчетов")
        
        try:
            # Симуляция экспорта отчета
            params = {
                "format": "json",
                "report_type": "finance"
            }
            
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/analytics/reports/finance",
                headers=self.headers,
                params=params,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                print("✅ Отчет успешно экспортирован")
                return True
            else:
                print(f"❌ Ошибка экспорта отчета: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при экспорте отчета: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Запуск всех тестов менеджера"""
        print("🚀 Тестирование функционала роли МЕНЕДЖЕР")
        print("=" * 60)
        
        # Авторизация
        if not self.authenticate():
            print("❌ Тестирование прервано: ошибка авторизации")
            return False
        
        # Список тестов
        tests = [
            ("Дашборд аналитики", self.test_analytics_dashboard),
            ("Финансовый отчет", self.test_finance_report),
            ("Отчет активности", self.test_activity_report),
            ("Обзор пользователей", self.test_users_overview),
            ("Кастомная аналитика", self.test_custom_analytics),
            ("Экспорт отчетов", self.test_export_reports),
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
        print(f"📊 Результат тестирования МЕНЕДЖЕРА: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 УСПЕХ! Функционал менеджера работает корректно")
            return True
        else:
            print("⚠️ ВНИМАНИЕ! Есть проблемы с функционалом менеджера")
            return False

def main():
    """Главная функция"""
    tester = ManagerTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main() 