#!/usr/bin/env python3
"""
Тест 1: Настройка тестовых пользователей
Создает пользователей для всех 5 ролей в системе страхования
"""

import requests
import json
from typing import Dict, Any

# Конфигурация
AUTH_BASE_URL = "http://localhost:8001"
BACKEND_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Тестовые пользователи для каждой роли
TEST_USERS = {
    "agent": {
        "username": "test_agent",
        "email": "agent@test.com",
        "password": "TestAgent123!",
        "full_name": "Тестовый Агент",
        "role": "agent"
    },
    "adjuster": {
        "username": "test_adjuster", 
        "email": "adjuster@test.com",
        "password": "TestAdjuster123!",
        "full_name": "Тестовый Урегулировщик",
        "role": "adjuster"
    },
    "operator": {
        "username": "test_operator",
        "email": "operator@test.com", 
        "password": "TestOperator123!",
        "full_name": "Тестовый Оператор",
        "role": "operator"
    },
    "manager": {
        "username": "test_manager",
        "email": "manager@test.com",
        "password": "TestManager123!",
        "full_name": "Тестовый Менеджер", 
        "role": "manager"
    },
    "admin": {
        "username": "test_admin",
        "email": "admin@test.com",
        "password": "TestAdmin123!",
        "full_name": "Тестовый Администратор",
        "role": "admin"
    }
}

def check_services_availability():
    """Проверка доступности сервисов"""
    print("🔍 Проверка доступности сервисов...")
    
    try:
        # Проверка auth-service
        response = requests.get(f"{AUTH_BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Auth-service доступен")
        else:
            print(f"⚠️ Auth-service вернул код {response.status_code}")
    except Exception as e:
        print(f"❌ Auth-service недоступен: {e}")
        return False
    
    try:
        # Проверка backend
        response = requests.get(f"{BACKEND_BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Backend доступен")
        else:
            print(f"⚠️ Backend вернул код {response.status_code}")
    except Exception as e:
        print(f"❌ Backend недоступен: {e}")
        return False
    
    return True

def register_user(user_data: Dict[str, Any]) -> bool:
    """Регистрация пользователя"""
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/register",
            json=user_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            print(f"✅ Пользователь {user_data['username']} ({user_data['role']}) создан успешно")
            return True
        elif response.status_code == 400:
            # Возможно пользователь уже существует
            try:
                error_detail = response.json().get('detail', 'Неизвестная ошибка')
                if "already exists" in error_detail.lower() or "уже существует" in error_detail.lower():
                    print(f"⚠️ Пользователь {user_data['username']} уже существует")
                    return True
                else:
                    print(f"❌ Ошибка создания {user_data['username']}: {error_detail}")
                    return False
            except:
                print(f"❌ Ошибка создания {user_data['username']}: {response.text}")
                return False
        else:
            print(f"❌ Ошибка создания {user_data['username']}: HTTP {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при создании {user_data['username']}: {e}")
        return False

def verify_user_login(username: str, password: str, role: str) -> bool:
    """Проверка возможности входа пользователя"""
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/login",
            data=login_data,  # form-data для OAuth2
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print(f"✅ Вход {username} ({role}) успешен")
                return True
            else:
                print(f"❌ Отсутствует токен в ответе для {username}")
                return False
        else:
            print(f"❌ Ошибка входа {username}: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при входе {username}: {e}")
        return False

def main():
    """Основная функция настройки тестовых пользователей"""
    print("🚀 Настройка тестовых пользователей для системы страхования")
    print("=" * 70)
    
    # Проверка доступности сервисов
    if not check_services_availability():
        print("❌ Сервисы недоступны. Завершение.")
        return False
    
    print("\n📝 Создание тестовых пользователей...")
    
    success_count = 0
    total_users = len(TEST_USERS)
    
    # Создание пользователей
    for role, user_data in TEST_USERS.items():
        print(f"\n👤 Создание пользователя роли {role.upper()}:")
        if register_user(user_data):
            success_count += 1
    
    print(f"\n📊 Результат создания пользователей: {success_count}/{total_users}")
    
    # Проверка входа для созданных пользователей
    print("\n🔐 Проверка возможности входа...")
    
    login_success_count = 0
    for role, user_data in TEST_USERS.items():
        if verify_user_login(user_data["username"], user_data["password"], role):
            login_success_count += 1
    
    print(f"\n📊 Результат проверки входа: {login_success_count}/{total_users}")
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    if success_count == total_users and login_success_count == total_users:
        print("🎉 УСПЕХ! Все тестовые пользователи созданы и готовы к работе")
        print("\n📋 Доступные тестовые аккаунты:")
        for role, user_data in TEST_USERS.items():
            print(f"   {role.upper()}: {user_data['username']} / {user_data['password']}")
        return True
    else:
        print("⚠️ ЧАСТИЧНЫЙ УСПЕХ. Некоторые пользователи не созданы или недоступны")
        return False

if __name__ == "__main__":
    main() 