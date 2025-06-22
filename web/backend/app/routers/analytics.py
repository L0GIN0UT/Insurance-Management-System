from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
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
    analytics_service = AnalyticsService(db)
    dashboard_data = analytics_service.get_dashboard_data()
    return dashboard_data

@router.get("/reports/finance", response_model=FinanceReportData)
async def get_finance_report(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate financial report"""
    analytics_service = AnalyticsService(db)
    report = analytics_service.generate_finance_report(start_date, end_date)
    return report

@router.get("/reports/activity", response_model=ActivityReportData)
async def get_activity_report(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Generate activity report"""
    analytics_service = AnalyticsService(db)
    report = analytics_service.generate_activity_report(start_date, end_date)
    return report

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