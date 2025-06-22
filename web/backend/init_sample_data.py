#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных в базе данных страхования
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.db.models import InsuranceProduct, Client, Contract, Claim, ContractStatus, ClaimStatus
from app.db.database import create_tables
from datetime import date, datetime, timedelta

def init_sample_data():
    """Создает полный набор тестовых данных"""
    settings = get_settings()
    
    # Create database engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Ensure tables exist
    create_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_products = db.query(InsuranceProduct).count()
        existing_clients = db.query(Client).count()
        
        if existing_products > 0 and existing_clients > 0:
            print(f"✅ База данных уже содержит данные: {existing_products} продуктов, {existing_clients} клиентов")
            return
        
        # 1. Create Insurance Products
        sample_products = [
            {
                "name": "Автострахование ОСАГО",
                "description": "Обязательное страхование автогражданской ответственности",
                "base_premium": 5000.0,
                "coverage_amount": 400000.0,
                "is_active": True
            },
            {
                "name": "Автострахование КАСКО",
                "description": "Добровольное страхование автомобиля от ущерба, хищения и угона",
                "base_premium": 35000.0,
                "coverage_amount": 1500000.0,
                "is_active": True
            },
            {
                "name": "Страхование недвижимости",
                "description": "Страхование квартир, домов и коммерческой недвижимости",
                "base_premium": 8000.0,
                "coverage_amount": 3000000.0,
                "is_active": True
            },
            {
                "name": "Медицинское страхование",
                "description": "Добровольное медицинское страхование (ДМС)",
                "base_premium": 25000.0,
                "coverage_amount": 500000.0,
                "is_active": True
            },
            {
                "name": "Страхование путешествий",
                "description": "Страхование от несчастных случаев и медицинских расходов в поездках",
                "base_premium": 1500.0,
                "coverage_amount": 100000.0,
                "is_active": True
            }
        ]
        
        products = []
        for product_data in sample_products:
            product = InsuranceProduct(**product_data)
            db.add(product)
            products.append(product)
        
        db.flush()  # Получаем ID продуктов
        
        # 2. Create Test Clients
        sample_clients = [
            {
                "first_name": "Иван",
                "last_name": "Петров",
                "email": "ivan.petrov@example.com",
                "phone": "+7 (495) 123-45-67",
                "address": "г. Москва, ул. Тверская, д. 10, кв. 25",
                "date_of_birth": date(1985, 3, 15),
                "identification_number": "1234567890",
                "created_by": 1
            },
            {
                "first_name": "Мария",
                "last_name": "Сидорова",
                "email": "maria.sidorova@example.com",
                "phone": "+7 (495) 234-56-78",
                "address": "г. Москва, ул. Арбат, д. 25, кв. 12",
                "date_of_birth": date(1990, 7, 22),
                "identification_number": "2345678901",
                "created_by": 1
            },
            {
                "first_name": "Алексей",
                "last_name": "Козлов",
                "email": "alexey.kozlov@example.com",
                "phone": "+7 (495) 345-67-89",
                "address": "г. Москва, ул. Ленина, д. 45, кв. 8",
                "date_of_birth": date(1982, 11, 8),
                "identification_number": "3456789012",
                "created_by": 1
            },
            {
                "first_name": "Елена",
                "last_name": "Волкова",
                "email": "elena.volkova@example.com",
                "phone": "+7 (495) 456-78-90",
                "address": "г. Москва, ул. Пушкина, д. 33, кв. 55",
                "date_of_birth": date(1988, 5, 12),
                "identification_number": "4567890123",
                "created_by": 1
            }
        ]
        
        clients = []
        for client_data in sample_clients:
            client = Client(**client_data)
            db.add(client)
            clients.append(client)
        
        db.flush()  # Получаем ID клиентов
        
        # 3. Create Test Contracts (ACTIVE status for testing)
        sample_contracts = [
            {
                "contract_number": "CON-2024-001",
                "client_id": clients[0].id,
                "product_id": products[0].id,  # ОСАГО
                "agent_id": 1,
                "premium_amount": 5500.0,
                "coverage_amount": 400000.0,
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),
                "status": ContractStatus.ACTIVE,  # АКТИВНЫЙ для тестирования
                "terms_conditions": "Стандартные условия ОСАГО"
            },
            {
                "contract_number": "CON-2024-002",
                "client_id": clients[1].id,
                "product_id": products[1].id,  # КАСКО
                "agent_id": 1,
                "premium_amount": 38000.0,
                "coverage_amount": 1500000.0,
                "start_date": date(2024, 2, 1),
                "end_date": date(2025, 2, 1),
                "status": ContractStatus.ACTIVE,  # АКТИВНЫЙ для тестирования
                "terms_conditions": "Полное КАСКО с франшизой 15000 руб"
            },
            {
                "contract_number": "CON-2024-003",
                "client_id": clients[2].id,
                "product_id": products[2].id,  # Недвижимость
                "agent_id": 1,
                "premium_amount": 8500.0,
                "coverage_amount": 3000000.0,
                "start_date": date(2024, 3, 1),
                "end_date": date(2025, 3, 1),
                "status": ContractStatus.ACTIVE,  # АКТИВНЫЙ для тестирования
                "terms_conditions": "Страхование квартиры от пожара и затопления"
            },
            {
                "contract_number": "CON-2024-004",
                "client_id": clients[3].id,
                "product_id": products[3].id,  # ДМС
                "agent_id": 1,
                "premium_amount": 27000.0,
                "coverage_amount": 500000.0,
                "start_date": date(2024, 4, 1),
                "end_date": date(2025, 4, 1),
                "status": ContractStatus.ACTIVE,  # АКТИВНЫЙ для тестирования
                "terms_conditions": "ДМС с включением стоматологии"
            }
        ]
        
        contracts = []
        for contract_data in sample_contracts:
            contract = Contract(**contract_data)
            db.add(contract)
            contracts.append(contract)
        
        db.flush()  # Получаем ID договоров
        
        # 4. Create Test Claims for adjuster testing
        sample_claims = [
            {
                "claim_number": "CLM-2024-001",
                "contract_id": contracts[0].id,  # ОСАГО
                "incident_date": date(2024, 6, 15),
                "reported_date": date(2024, 6, 16),
                "description": "ДТП на перекрестке ул. Тверская - ул. Пушкина. Повреждение переднего бампера.",
                "claim_amount": 25000.0,
                "status": ClaimStatus.SUBMITTED,
                "adjuster_id": None
            },
            {
                "claim_number": "CLM-2024-002",
                "contract_id": contracts[1].id,  # КАСКО
                "incident_date": date(2024, 6, 20),
                "reported_date": date(2024, 6, 21),
                "description": "Угон автомобиля с парковки торгового центра.",
                "claim_amount": 1200000.0,
                "status": ClaimStatus.UNDER_REVIEW,
                "adjuster_id": 2  # Предполагаем ID урегулировщика
            },
            {
                "claim_number": "CLM-2024-003",
                "contract_id": contracts[2].id,  # Недвижимость
                "incident_date": date(2024, 6, 25),
                "reported_date": date(2024, 6, 26),
                "description": "Затопление квартиры из-за прорыва трубы у соседей сверху.",
                "claim_amount": 150000.0,
                "approved_amount": 145000.0,
                "status": ClaimStatus.APPROVED,
                "adjuster_id": 2,
                "adjuster_notes": "Заявка одобрена. Ущерб подтвержден экспертизой."
            }
        ]
        
        claims = []
        for claim_data in sample_claims:
            claim = Claim(**claim_data)
            db.add(claim)
            claims.append(claim)
        
        # Commit all changes
        db.commit()
        
        print("✅ Успешно созданы тестовые данные:")
        print(f"   - {len(products)} страховых продуктов")
        print(f"   - {len(clients)} клиентов")
        print(f"   - {len(contracts)} активных договоров")
        print(f"   - {len(claims)} заявок")
        
        print(f"\n🎉 Всего создано полноценных тестовых данных!")
        print("\n📋 Теперь можно тестировать:")
        print("   1. Агенты: создание клиентов и договоров")
        print("   2. Операторы: создание заявок по активным договорам")
        print("   3. Урегулировщики: обработка существующих заявок")
        print("   4. Менеджеры: аналитика по данным")
        print("   5. Администраторы: управление пользователями")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Backward compatibility
def init_sample_products():
    """Обратная совместимость - вызывает полную инициализацию"""
    init_sample_data()

if __name__ == "__main__":
    init_sample_data() 