from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta
from app.utils.auth import get_current_user, require_roles
from app.db.database import get_db
from app.schemas.reports import FinanceReportData, ActivityReportData
from app.functions.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Get dashboard analytics data"""
    
    # Получаем актуальные данные из базы
    from app.db.models import Client, Contract, Claim, ContractStatus, ClaimStatus
    from sqlalchemy import func
    
    # Статистика клиентов
    total_clients = db.query(Client).count()
    active_clients = total_clients  # Все клиенты считаются активными
    
    # Статистика за текущий месяц
    today = date.today()
    month_start = today.replace(day=1)
    new_clients_this_month = db.query(Client).filter(
        Client.created_at >= month_start
    ).count()
    
    # Статистика договоров
    total_contracts = db.query(Contract).count()
    active_contracts = db.query(Contract).filter(
        Contract.status == ContractStatus.ACTIVE
    ).count()
    expired_contracts = db.query(Contract).filter(
        Contract.status == ContractStatus.EXPIRED
    ).count()
    
    # Статистика заявок
    total_claims = db.query(Claim).count()
    pending_claims = db.query(Claim).filter(
        Claim.status.in_(['submitted', 'under_review'])
    ).count()
    approved_claims = db.query(Claim).filter(
        Claim.status == 'approved'
    ).count()
    rejected_claims = db.query(Claim).filter(
        Claim.status == 'rejected'
    ).count()
    
    # Статистика выручки
    total_revenue = db.query(func.sum(Contract.premium_amount)).scalar() or 0
    monthly_revenue = db.query(func.sum(Contract.premium_amount)).filter(
        Contract.created_at >= month_start
    ).scalar() or 0
    
    return {
        "clients": {
            "total": total_clients,
            "active": active_clients,
            "new_this_month": new_clients_this_month
        },
        "contracts": {
            "total": total_contracts,
            "active": active_contracts,
            "expired": expired_contracts
        },
        "claims": {
            "total": total_claims,
            "pending": pending_claims,
            "approved": approved_claims,
            "rejected": rejected_claims
        },
        "revenue": {
            "total": float(total_revenue),
            "monthly": float(monthly_revenue)
        }
    }

@router.get("/reports/finance", response_model=FinanceReportData)
async def get_finance_report(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate financial report"""
    analytics_service = AnalyticsService(db)
    
    # Устанавливаем дефолтные даты если не указаны
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date.today() - timedelta(days=90)  # последние 3 месяца
    
    from app.db.models import Contract, Claim, InsuranceProduct
    from sqlalchemy import func, and_, extract
    
    # Получаем договоры за период
    contracts = db.query(Contract).filter(
        and_(
            Contract.created_at >= start_date,
            Contract.created_at <= end_date
        )
    ).all()
    
    # Получаем выплаченные заявки за период
    paid_claims = db.query(Claim).filter(
        and_(
            Claim.updated_at >= start_date,
            Claim.updated_at <= end_date,
            Claim.status == 'approved'
        )
    ).all()
    
    total_premiums = sum(c.premium_amount for c in contracts)
    total_claims = sum(c.approved_amount or 0 for c in paid_claims)
    profit = total_premiums - total_claims
    
    # Помесячная разбивка
    monthly_data = {}
    for contract in contracts:
        month_key = contract.created_at.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'premiums': 0, 'claims': 0, 'profit': 0}
        monthly_data[month_key]['premiums'] += contract.premium_amount
    
    for claim in paid_claims:
        month_key = claim.updated_at.strftime('%Y-%m')
        if month_key in monthly_data:
            monthly_data[month_key]['claims'] += claim.approved_amount or 0
    
    # Вычисляем прибыль по месяцам
    for month in monthly_data:
        monthly_data[month]['profit'] = monthly_data[month]['premiums'] - monthly_data[month]['claims']
    
    by_month = [
        {
            'month': month,
            'premiums': data['premiums'],
            'claims': data['claims'],
            'profit': data['profit']
        }
        for month, data in sorted(monthly_data.items())
    ]
    
    # По продуктам
    product_data = {}
    for contract in contracts:
        product_id = contract.product_id
        if product_id not in product_data:
            product = db.query(InsuranceProduct).filter(InsuranceProduct.id == product_id).first()
            product_data[product_id] = {
                'product_name': product.name if product else f'Product {product_id}',
                'premiums': 0,
                'claims': 0,
                'count': 0
            }
        product_data[product_id]['premiums'] += contract.premium_amount
        product_data[product_id]['count'] += 1
    
    # Добавляем данные по заявкам к продуктам
    for claim in paid_claims:
        if hasattr(claim, 'contract') and claim.contract:
            product_id = claim.contract.product_id
            if product_id in product_data:
                product_data[product_id]['claims'] += claim.approved_amount or 0
    
    by_product = list(product_data.values())
    
    return FinanceReportData(
        total_premiums=total_premiums,
        total_claims=total_claims,
        profit=profit,
        period={"start": start_date.isoformat(), "end": end_date.isoformat()},
        by_month=by_month,
        by_product=by_product
    )

@router.get("/reports/activity", response_model=ActivityReportData)
async def get_activity_report(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate activity report"""
    analytics_service = AnalyticsService(db)
    
    # Устанавливаем дефолтные даты если не указаны
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date.today() - timedelta(days=90)
    
    # Имитируем данные о пользователях (так как у нас нет прямого доступа к auth-service)
    total_users = 25  # Пример
    active_users = 18  # Пример
    
    # Статистика по ролям
    by_role = [
        {"role": "agent", "count": 8, "active": 6},
        {"role": "adjuster", "count": 4, "active": 3},
        {"role": "operator", "count": 6, "active": 5},
        {"role": "manager", "count": 3, "active": 2},
        {"role": "admin", "count": 4, "active": 2}
    ]
    
    # Топ агентов по договорам
    from app.db.models import Contract
    from sqlalchemy import func, and_
    
    agent_stats = db.query(
        Contract.agent_id,
        func.count(Contract.id).label('contracts_count'),
        func.sum(Contract.premium_amount).label('total_premium')
    ).filter(
        and_(
            Contract.created_at >= start_date,
            Contract.created_at <= end_date,
            Contract.agent_id.isnot(None)
        )
    ).group_by(Contract.agent_id).order_by(
        func.sum(Contract.premium_amount).desc()
    ).limit(10).all()
    
    top_agents = [
        {
            'agent_name': f'Агент {stat.agent_id}',  # В реальности нужно получать из auth-service
            'contracts_count': stat.contracts_count,
            'total_premium': float(stat.total_premium)
        }
        for stat in agent_stats
    ]
    
    return ActivityReportData(
        total_users=total_users,
        active_users=active_users,
        by_role=by_role,
        top_agents=top_agents
    )

@router.get("/reports/contracts")
async def get_contracts_report(
    start_date: date = None,
    end_date: date = None,
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate contracts report"""
    # TODO: Implement contracts report logic
    return {
        "report_type": "contracts",
        "period": {"start": start_date, "end": end_date},
        "data": []
    }

@router.get("/reports/claims")
async def get_claims_report(
    start_date: date = None,
    end_date: date = None,
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate claims report"""
    # TODO: Implement claims report logic
    return {
        "report_type": "claims",
        "period": {"start": start_date, "end": end_date},
        "data": []
    }

@router.get("/reports/revenue")
async def get_revenue_report(
    start_date: date = None,
    end_date: date = None,
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate revenue report"""
    # TODO: Implement revenue report logic
    return {
        "report_type": "revenue",
        "period": {"start": start_date, "end": end_date},
        "total_revenue": 0,
        "by_month": [],
        "by_product": []
    }

@router.get("/statistics/overview")
async def get_overview_statistics(
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Get overview statistics"""
    # TODO: Implement overview statistics logic
    return {
        "clients": {"total": 0, "active": 0, "new_this_month": 0},
        "contracts": {"total": 0, "active": 0, "expired": 0},
        "claims": {"total": 0, "pending": 0, "approved": 0, "rejected": 0},
        "agents_performance": []
    } 