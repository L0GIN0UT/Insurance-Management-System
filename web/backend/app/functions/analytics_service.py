from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from ..db.models import Client, Contract, Claim, InsuranceProduct, ContractStatus, ClaimStatus
from ..modules.analytics import (
    AnalyticsRequest, SalesMetrics, ClaimsMetrics, FinancialMetrics, 
    PerformanceMetrics, DashboardSummary, ChartData, TimeRange
)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_sales_analytics(self, request: AnalyticsRequest) -> SalesMetrics:
        """Generate sales analytics"""
        contracts_query = self.db.query(Contract).filter(
            and_(
                Contract.created_at >= request.start_date,
                Contract.created_at <= request.end_date
            )
        )
        
        contracts = contracts_query.all()
        
        total_contracts = len(contracts)
        total_premium = sum(c.premium_amount for c in contracts)
        average_premium = total_premium / total_contracts if total_contracts > 0 else 0
        
        active_contracts = len([c for c in contracts if c.status == ContractStatus.ACTIVE])
        conversion_rate = active_contracts / total_contracts if total_contracts > 0 else 0
        
        # Top products
        product_sales = {}
        for contract in contracts:
            product_id = contract.product_id
            if product_id in product_sales:
                product_sales[product_id]['count'] += 1
                product_sales[product_id]['premium'] += contract.premium_amount
            else:
                product_sales[product_id] = {
                    'product_id': product_id,
                    'count': 1,
                    'premium': contract.premium_amount,
                    'product_name': contract.product.name if contract.product else 'Unknown'
                }
        
        top_products = sorted(product_sales.values(), key=lambda x: x['premium'], reverse=True)[:5]
        
        # Sales by agent
        agent_sales = {}
        for contract in contracts:
            agent_id = contract.agent_id
            if agent_id in agent_sales:
                agent_sales[agent_id]['count'] += 1
                agent_sales[agent_id]['premium'] += contract.premium_amount
            else:
                agent_sales[agent_id] = {
                    'agent_id': agent_id,
                    'count': 1,
                    'premium': contract.premium_amount
                }
        
        sales_by_agent = sorted(agent_sales.values(), key=lambda x: x['premium'], reverse=True)
        
        return SalesMetrics(
            total_contracts=total_contracts,
            total_premium=total_premium,
            average_premium=average_premium,
            conversion_rate=conversion_rate,
            top_products=top_products,
            sales_by_agent=sales_by_agent
        )

    def get_claims_analytics(self, request: AnalyticsRequest) -> ClaimsMetrics:
        """Generate claims analytics"""
        # Base query for claims in date range
        claims_query = self.db.query(Claim).filter(
            and_(
                Claim.created_at >= request.start_date,
                Claim.created_at <= request.end_date
            )
        )
        
        claims = claims_query.all()
        
        # Calculate metrics
        total_claims = len(claims)
        total_claimed_amount = sum(c.claim_amount or 0 for c in claims)
        total_approved_amount = sum(c.approved_amount or 0 for c in claims if c.approved_amount)
        average_claim_amount = total_claimed_amount / total_claims if total_claims > 0 else 0
        
        approved_claims = len([c for c in claims if c.status == ClaimStatus.APPROVED])
        approval_rate = approved_claims / total_claims if total_claims > 0 else 0
        
        # Claims by status
        claims_by_status = {}
        for status in ClaimStatus:
            claims_by_status[status.value] = len([c for c in claims if c.status == status])
        
        # Claims by adjuster
        adjuster_claims = {}
        for claim in claims:
            if claim.adjuster_id:
                adjuster_id = claim.adjuster_id
                if adjuster_id in adjuster_claims:
                    adjuster_claims[adjuster_id]['count'] += 1
                    adjuster_claims[adjuster_id]['total_amount'] += claim.claim_amount or 0
                else:
                    adjuster_claims[adjuster_id] = {
                        'adjuster_id': adjuster_id,
                        'count': 1,
                        'total_amount': claim.claim_amount or 0
                    }
        
        claims_by_adjuster = list(adjuster_claims.values())
        
        return ClaimsMetrics(
            total_claims=total_claims,
            total_claimed_amount=total_claimed_amount,
            total_approved_amount=total_approved_amount,
            average_claim_amount=average_claim_amount,
            approval_rate=approval_rate,
            claims_by_status=claims_by_status,
            claims_by_adjuster=claims_by_adjuster
        )

    def get_financial_analytics(self, request: AnalyticsRequest) -> FinancialMetrics:
        """Generate financial analytics"""
        # Revenue from contracts
        contracts = self.db.query(Contract).filter(
            and_(
                Contract.created_at >= request.start_date,
                Contract.created_at <= request.end_date
            )
        ).all()
        
        total_revenue = sum(c.premium_amount for c in contracts)
        
        # Claims paid in the period
        paid_claims = self.db.query(Claim).filter(
            and_(
                Claim.updated_at >= request.start_date,
                Claim.updated_at <= request.end_date,
                Claim.status == ClaimStatus.PAID
            )
        ).all()
        
        total_claims_paid = sum(c.approved_amount or 0 for c in paid_claims)
        
        # Calculate metrics
        profit_margin = (total_revenue - total_claims_paid) / total_revenue if total_revenue > 0 else 0
        expense_ratio = total_claims_paid / total_revenue if total_revenue > 0 else 0
        
        # Revenue by product
        product_revenue = {}
        for contract in contracts:
            product_id = contract.product_id
            if product_id in product_revenue:
                product_revenue[product_id]['revenue'] += contract.premium_amount
            else:
                product_revenue[product_id] = {
                    'product_id': product_id,
                    'product_name': contract.product.name if contract.product else 'Unknown',
                    'revenue': contract.premium_amount
                }
        
        revenue_by_product = sorted(product_revenue.values(), key=lambda x: x['revenue'], reverse=True)
        
        # Monthly revenue breakdown
        monthly_revenue = self._get_monthly_breakdown(contracts, request.start_date, request.end_date)
        
        return FinancialMetrics(
            total_revenue=total_revenue,
            total_claims_paid=total_claims_paid,
            profit_margin=profit_margin,
            expense_ratio=expense_ratio,
            revenue_by_product=revenue_by_product,
            monthly_revenue=monthly_revenue
        )

    def get_performance_analytics(self, request: AnalyticsRequest) -> PerformanceMetrics:
        """Generate performance analytics"""
        # Agent performance
        agent_performance = self._get_agent_performance(request.start_date, request.end_date)
        
        # Adjuster performance
        adjuster_performance = self._get_adjuster_performance(request.start_date, request.end_date)
        
        # Product performance
        product_performance = self._get_product_performance(request.start_date, request.end_date)
        
        return PerformanceMetrics(
            agent_performance=agent_performance,
            adjuster_performance=adjuster_performance,
            product_performance=product_performance
        )

    def get_dashboard_summary(self) -> DashboardSummary:
        """Get dashboard summary for current state"""
        active_contracts = self.db.query(Contract).filter(
            Contract.status == ContractStatus.ACTIVE
        ).count()
        
        pending_claims = self.db.query(Claim).filter(
            Claim.status.in_([ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW])
        ).count()
        
        today = date.today()
        month_start = today.replace(day=1)
        total_revenue_mtd = self.db.query(func.sum(Contract.premium_amount)).filter(
            and_(
                Contract.created_at >= month_start,
                Contract.created_at <= today
            )
        ).scalar() or 0
        
        total_claims_amount = self.db.query(func.sum(Claim.approved_amount)).filter(
            Claim.status == ClaimStatus.APPROVED
        ).scalar() or 0
        
        total_premiums = self.db.query(func.sum(Contract.premium_amount)).scalar() or 0
        claims_ratio = total_claims_amount / total_premiums if total_premiums > 0 else 0
        
        return DashboardSummary(
            active_contracts=active_contracts,
            pending_claims=pending_claims,
            total_revenue_mtd=total_revenue_mtd,
            claims_ratio=claims_ratio,
            top_performing_agent=None,
            recent_activities=[],
            alerts=[]
        )

    def _get_monthly_breakdown(self, contracts: List[Contract], start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get monthly revenue breakdown"""
        monthly_data = {}
        
        for contract in contracts:
            month_key = contract.created_at.strftime('%Y-%m')
            if month_key in monthly_data:
                monthly_data[month_key] += contract.premium_amount
            else:
                monthly_data[month_key] = contract.premium_amount
        
        return [
            {'month': month, 'revenue': revenue}
            for month, revenue in sorted(monthly_data.items())
        ]

    def _get_agent_performance(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get agent performance metrics"""
        agent_stats = self.db.query(
            Contract.agent_id,
            func.count(Contract.id).label('contract_count'),
            func.sum(Contract.premium_amount).label('total_premium'),
            func.avg(Contract.premium_amount).label('avg_premium')
        ).filter(
            and_(
                Contract.created_at >= start_date,
                Contract.created_at <= end_date
            )
        ).group_by(Contract.agent_id).all()
        
        return [
            {
                'agent_id': stat.agent_id,
                'contract_count': stat.contract_count,
                'total_premium': float(stat.total_premium),
                'avg_premium': float(stat.avg_premium)
            }
            for stat in agent_stats
        ]

    def _get_adjuster_performance(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get adjuster performance metrics"""
        adjuster_stats = self.db.query(
            Claim.adjuster_id,
            func.count(Claim.id).label('claim_count'),
            func.sum(Claim.approved_amount).label('total_approved'),
            func.avg(Claim.approved_amount).label('avg_approved')
        ).filter(
            and_(
                Claim.updated_at >= start_date,
                Claim.updated_at <= end_date,
                Claim.adjuster_id.isnot(None)
            )
        ).group_by(Claim.adjuster_id).all()
        
        return [
            {
                'adjuster_id': stat.adjuster_id,
                'claim_count': stat.claim_count,
                'total_approved': float(stat.total_approved or 0),
                'avg_approved': float(stat.avg_approved or 0)
            }
            for stat in adjuster_stats
        ]

    def _get_product_performance(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get product performance metrics"""
        product_stats = self.db.query(
            Contract.product_id,
            func.count(Contract.id).label('contract_count'),
            func.sum(Contract.premium_amount).label('total_premium')
        ).filter(
            and_(
                Contract.created_at >= start_date,
                Contract.created_at <= end_date
            )
        ).group_by(Contract.product_id).all()
        
        performance = []
        for stat in product_stats:
            product = self.db.query(InsuranceProduct).filter(
                InsuranceProduct.id == stat.product_id
            ).first()
            
            performance.append({
                'product_id': stat.product_id,
                'product_name': product.name if product else 'Unknown',
                'contract_count': stat.contract_count,
                'total_premium': float(stat.total_premium)
            })
        
        return sorted(performance, key=lambda x: x['total_premium'], reverse=True) 