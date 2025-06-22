#!/usr/bin/env python3
"""
Тест 2: Функционал роли АГЕНТ
Тестирует полный функционал агента с авторизацией:
- Управление клиентами (создание, просмотр, редактирование)
- Управление договорами (создание, просмотр, расчет премии)
"""

import requests
import json
from typing import Dict, Any, Optional
import time

# Конфигурация
AUTH_BASE_URL = "http://localhost:8001"
BACKEND_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Данные тестового агента
AGENT_CREDENTIALS = {
    "username": "test_agent",
    "password": "TestAgent123!"
}

class AgentTester:
    def __init__(self):
        self.token = None
        self.headers = None
        self.test_client_id = None
        self.test_contract_id = None
        self.product_id = None  # Реальный ID продукта
    
    def authenticate(self) -> bool:
        """Авторизация агента"""
        print("🔐 Авторизация агента...")
        
        try:
            response = requests.post(
                f"{AUTH_BASE_URL}/auth/login",
                data={
                    "username": "test_agent",
                    "password": "TestAgent123!"
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Авторизация успешна")
                return True
            else:
                print(f"❌ Ошибка авторизации: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при авторизации: {e}")
            return False
    
    def get_first_product_id(self) -> bool:
        """Получение ID первого доступного продукта"""
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/products/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                products = response.json()
                if products and len(products) > 0:
                    self.product_id = products[0]["id"]
                    print(f"📦 Найден продукт ID: {self.product_id} - {products[0]['name']}")
                    return True
                else:
                    print("❌ Продукты не найдены")
                    return False
            else:
                print(f"❌ Ошибка получения продуктов: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении продуктов: {e}")
            return False
    
    def test_get_clients(self) -> bool:
        """Тест получения списка клиентов"""
        print("\n📋 Тест: Получение списка клиентов")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/clients/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                clients = response.json()
                print(f"✅ Получен список клиентов: {len(clients)} записей")
                return True
            else:
                print(f"❌ Ошибка получения клиентов: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении клиентов: {e}")
            return False
    
    def test_create_client(self) -> bool:
        """Тест создания нового клиента"""
        print("\n👤 Тест: Создание нового клиента")
        
        timestamp = int(time.time())
        
        client_data = {
            "first_name": "Тестовый",
            "last_name": "Клиент Агента",
            "email": f"agent_client_{timestamp}@test.com",
            "phone": "+7999123456",
            "address": "Тестовый адрес, 123",
            "date_of_birth": "1990-01-01"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/clients/",
                json=client_data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                created_client = response.json()
                self.test_client_id = created_client["id"]
                print(f"✅ Клиент создан: {created_client['first_name']} {created_client['last_name']} (ID: {self.test_client_id})")
                return True
            else:
                print(f"❌ Ошибка создания клиента: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при создании клиента: {e}")
            return False
    
    def test_get_client(self) -> bool:
        """Тест получения детальной информации о клиенте"""
        if not self.test_client_id:
            print("⚠️ Пропуск теста: клиент не создан")
            return False
            
        print(f"\n🔍 Тест: Получение информации о клиенте {self.test_client_id}")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/clients/{self.test_client_id}",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                client = response.json()
                print(f"✅ Информация о клиенте получена: {client.get('full_name')}")
                return True
            else:
                print(f"❌ Ошибка получения клиента: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении клиента: {e}")
            return False
    
    def test_get_contracts(self) -> bool:
        """Тест получения списка договоров"""
        print("\n📋 Тест: Получение списка договоров")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/contracts/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                contracts = response.json()
                print(f"✅ Получен список договоров: {len(contracts)} записей")
                return True
            else:
                print(f"❌ Ошибка получения договоров: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении договоров: {e}")
            return False
    
    def test_calculate_premium(self) -> bool:
        """Тест расчета премии"""
        print("\n💰 Тест: Расчет премии")
        
        calculation_data = {
            "product_id": self.product_id,
            "coverage_amount": 100000,
            "client_age": 30,
            "coverage_period": 12
        }
        
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/contracts/calculate",
                headers=self.headers,
                json=calculation_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                calculation = response.json()
                premium = calculation.get("premium_amount", 0)
                print(f"✅ Премия рассчитана: {premium} руб.")
                return True
            else:
                print(f"❌ Ошибка расчета премии: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при расчете премии: {e}")
            return False
    
    def test_create_contract(self) -> bool:
        """Тест создания нового договора"""
        if not self.test_client_id:
            print("⚠️ Пропуск теста: клиент не создан")
            return False
            
        print(f"\n📝 Тест: Создание договора для клиента {self.test_client_id}")
        
        contract_data = {
            "client_id": self.test_client_id,
            "product_id": self.product_id,
            "coverage_amount": 100000,
            "premium_amount": 5000,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/contracts/",
                headers=self.headers,
                json=contract_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                created_contract = response.json()
                self.test_contract_id = created_contract["id"]
                print(f"✅ Договор создан: {created_contract['contract_number']} (ID: {self.test_contract_id})")
                return True
            else:
                print(f"❌ Ошибка создания договора: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при создании договора: {e}")
            return False
    
    def test_get_contract(self) -> bool:
        """Тест получения детальной информации о договоре"""
        if not self.test_contract_id:
            print("⚠️ Пропуск теста: договор не создан")
            return False
            
        print(f"\n🔍 Тест: Получение информации о договоре {self.test_contract_id}")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/contracts/{self.test_contract_id}",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                contract = response.json()
                print(f"✅ Информация о договоре получена: сумма покрытия {contract.get('coverage_amount')}")
                return True
            else:
                print(f"❌ Ошибка получения договора: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении договора: {e}")
            return False
    
    def run_tests(self) -> None:
        """Запуск всех тестов агента"""
        print("🚀 Тестирование функционала роли АГЕНТ")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Не удалось авторизоваться")
            return
        
        if not self.get_first_product_id():
            print("❌ Не удалось получить ID продукта")
            return
        
        tests = [
            self.test_get_clients,
            self.test_create_client,
            self.test_get_client,
            self.test_get_contracts,
            self.test_calculate_premium,
            self.test_create_contract,
            self.test_get_contract
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Результат тестирования АГЕНТА: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 УСПЕХ! Функционал агента работает корректно")
        else:
            print("⚠️ ВНИМАНИЕ! Есть проблемы с функционалом агента")

def main():
    """Главная функция"""
    tester = AgentTester()
    tester.run_tests()

if __name__ == "__main__":
    main() 