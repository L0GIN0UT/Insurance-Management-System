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
from app.db.models import InsuranceProduct
from app.db.database import create_tables

def init_sample_products():
    """Создает примеры страховых продуктов"""
    settings = get_settings()
    
    # Create database engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Ensure tables exist
    create_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if products already exist
        existing_products = db.query(InsuranceProduct).count()
        if existing_products > 0:
            print(f"✅ База данных уже содержит {existing_products} страховых продуктов")
            return
        
        # Sample insurance products
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
        
        # Create products
        created_products = []
        for product_data in sample_products:
            product = InsuranceProduct(**product_data)
            db.add(product)
            created_products.append(product_data["name"])
        
        # Commit changes
        db.commit()
        
        print("✅ Успешно созданы тестовые страховые продукты:")
        for name in created_products:
            print(f"   - {name}")
        
        print(f"\n🎉 Всего создано: {len(created_products)} продуктов")
        print("\n📋 Теперь можно:")
        print("   1. Зарегистрировать пользователя с ролью 'agent'")
        print("   2. Создавать клиентов")
        print("   3. Рассчитывать премии для договоров")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_products() 