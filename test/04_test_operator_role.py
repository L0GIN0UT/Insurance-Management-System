#!/usr/bin/env python3
"""
Тест 4: Функционал роли ОПЕРАТОР
Тестирует полный функционал оператора с авторизацией:
- Просмотр клиентов
- Создание заявок
- Отправка заявок урегулировщику
- Просмотр заявок
"""

import requests
import json
from typing import Dict, Any, Optional

# Конфигурация
AUTH_BASE_URL = "http://localhost:8001"
BACKEND_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Данные тестового оператора
OPERATOR_CREDENTIALS = {
    "username": "test_operator",
    "password": "TestOperator123!"
}

class OperatorTester:
    def __init__(self):
        self.token = None
        self.headers = None
        self.test_client_id = None
        self.test_claim_id = None
        self.test_contract_id = None  # Реальный ID договора
        self.product_id = None  # Реальный ID продукта
    
    def authenticate(self) -> bool:
        """Авторизация оператора"""
        print("🔐 Авторизация оператора...")
        
        try:
            response = requests.post(
                f"{AUTH_BASE_URL}/auth/login",
                data={
                    "username": "test_operator",
                    "password": "TestOperator123!"
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
    
    def get_first_contract_id(self) -> bool:
        """Получение ID первого доступного договора"""
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/contracts/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                contracts_data = response.json()
                contracts = contracts_data.get("contracts", []) if isinstance(contracts_data, dict) else contracts_data
                
                if contracts and len(contracts) > 0:
                    self.test_contract_id = contracts[0]["id"]
                    print(f"📋 Найден договор ID: {self.test_contract_id}")
                    return True
                else:
                    print("❌ Договоры не найдены")
                    return False
            else:
                print(f"❌ Ошибка получения договоров: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении договоров: {e}")
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
                clients_data = response.json()
                clients = clients_data.get("clients", []) if isinstance(clients_data, dict) else clients_data
                print(f"✅ Получен список клиентов: {len(clients)} записей")
                
                # Сохраняем ID первого клиента для создания заявки
                if clients and len(clients) > 0:
                    self.test_client_id = clients[0].get("id")
                    print(f"📝 Сохранен ID клиента для тестов: {self.test_client_id}")
                
                return True
            else:
                print(f"❌ Ошибка получения клиентов: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении клиентов: {e}")
            return False
    
    def test_get_claims(self) -> bool:
        """Тест получения списка заявок"""
        print("\n📋 Тест: Получение списка заявок")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/claims/",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                claims_data = response.json()
                claims = claims_data.get("claims", []) if isinstance(claims_data, dict) else claims_data
                print(f"✅ Получен список заявок: {len(claims)} записей")
                return True
            else:
                print(f"❌ Ошибка получения заявок: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении заявок: {e}")
            return False
    
    def test_create_claim(self) -> bool:
        """Тест создания новой заявки"""
        print("\n📝 Тест: Создание новой заявки")
        
        if not self.test_contract_id:
            print("⚠️ Пропуск теста: договор не найден")
            return False
        
        claim_data = {
            "contract_id": self.test_contract_id,  # Используем реальный ID договора
            "incident_date": "2024-01-15",
            "description": "Тестовая заявка от оператора",
            "claim_amount": 5000
        }
        
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/claims/",
                headers=self.headers,
                json=claim_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                created_claim = response.json()
                self.test_claim_id = created_claim["id"]
                print(f"✅ Заявка создана: {created_claim['claim_number']} (ID: {self.test_claim_id})")
                return True
            else:
                print(f"❌ Ошибка создания заявки: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при создании заявки: {e}")
            return False
    
    def test_submit_claim(self) -> bool:
        """Тест отправки заявки урегулировщику"""
        print("\n📤 Тест: Отправка заявки урегулировщику")
        
        if not self.test_contract_id:
            print("⚠️ Пропуск теста: договор не найден")
            return False
        
        submit_data = {
            "contract_id": self.test_contract_id,  # Используем реальный ID договора
            "incident_date": "2024-01-15",
            "description": "Детальное описание инцидента для урегулировщика от оператора с достаточным количеством символов для валидации",
            "claim_amount": 5000,
            "documents": ["document1.pdf", "document2.pdf"],
            "priority": "normal",
            "customer_contact": "operator_test@example.com"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/v1/claims/submit",
                headers=self.headers,
                json=submit_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                submitted_claim = response.json()
                print(f"✅ Заявка отправлена урегулировщику (ID: {submitted_claim.get('claim_id')})")
                return True
            else:
                print(f"❌ Ошибка отправки заявки: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при отправке заявки: {e}")
            return False
    
    def test_get_claim_details(self) -> bool:
        """Тест получения детальной информации о заявке"""
        if not self.test_claim_id:
            print("⚠️ Пропуск теста: заявка не создана")
            return False
            
        print(f"\n🔍 Тест: Получение информации о заявке {self.test_claim_id}")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/claims/{self.test_claim_id}",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                claim = response.json()
                print(f"✅ Информация о заявке получена: сумма {claim.get('claim_amount', 0)}")
                return True
            else:
                print(f"❌ Ошибка получения заявки: HTTP {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при получении заявки: {e}")
            return False
    
    def test_search_clients(self) -> bool:
        """Тест поиска клиентов"""
        print("\n🔍 Тест: Поиск клиентов")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/clients/?search=test",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                clients_data = response.json()
                clients = clients_data.get("clients", []) if isinstance(clients_data, dict) else clients_data
                print(f"✅ Результаты поиска клиентов: {len(clients)} записей")
                return True
            else:
                print(f"❌ Ошибка поиска клиентов: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при поиске клиентов: {e}")
            return False
    
    def test_claims_filtering(self) -> bool:
        """Тест фильтрации заявок"""
        print("\n🔍 Тест: Фильтрация заявок по статусу")
        
        try:
            response = requests.get(
                f"{BACKEND_BASE_URL}/api/v1/claims/?status=submitted",
                headers=self.headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                claims_data = response.json()
                claims = claims_data.get("claims", []) if isinstance(claims_data, dict) else claims_data
                print(f"✅ Отфильтрованные заявки: {len(claims)} записей")
                return True
            else:
                print(f"❌ Ошибка фильтрации заявок: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при фильтрации заявок: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Запуск всех тестов оператора"""
        print("🚀 Тестирование функционала роли ОПЕРАТОР")
        print("=" * 60)
        
        # Авторизация
        if not self.authenticate():
            print("❌ Тестирование прервано: ошибка авторизации")
            return False
        
        if not self.get_first_product_id():
            print("❌ Не удалось получить ID продукта")
            return False
        
        if not self.get_first_contract_id():
            print("❌ Не удалось получить ID договора")
            return False
        
        # Список тестов
        tests = [
            ("Получение списка клиентов", self.test_get_clients),
            ("Получение списка заявок", self.test_get_claims),
            ("Создание новой заявки", self.test_create_claim),
            ("Отправка заявки урегулировщику", self.test_submit_claim),
            ("Поиск клиентов", self.test_search_clients),
            ("Фильтрация заявок по статусу", self.test_claims_filtering)
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
        print(f"📊 Результат тестирования ОПЕРАТОРА: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 УСПЕХ! Функционал оператора работает корректно")
            return True
        else:
            print("⚠️ ВНИМАНИЕ! Есть проблемы с функционалом оператора")
            return False

def main():
    """Главная функция"""
    tester = OperatorTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main() 