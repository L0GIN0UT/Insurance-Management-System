from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

class ReportType(str, Enum):
    SALES = "sales"
    CLAIMS = "claims" 
    FINANCIAL = "financial"
    PERFORMANCE = "performance"

class TimeRange(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

# Analytics request schema
class AnalyticsRequest(BaseModel):
    report_type: ReportType
    start_date: date
    end_date: date
    time_range: TimeRange = TimeRange.MONTH
    filters: Dict[str, Any] = {}
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

# Analytics response schemas
class MetricData(BaseModel):
    label: str
    value: float
    percentage_change: Optional[float] = None
    trend: Optional[str] = None

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]

class AnalyticsResponse(BaseModel):
    report_type: ReportType
    period: str
    metrics: List[MetricData]
    charts: List[ChartData]
    generated_at: datetime

# Sales analytics
class SalesMetrics(BaseModel):
    total_contracts: int
    total_premium: float
    average_premium: float
    conversion_rate: float
    top_products: List[Dict[str, Any]]
    sales_by_agent: List[Dict[str, Any]]

class SalesAnalyticsResponse(BaseModel):
    period: str
    metrics: SalesMetrics
    charts: List[ChartData]
    generated_at: datetime

# Claims analytics
class ClaimsMetrics(BaseModel):
    total_claims: int
    total_claimed_amount: float
    total_approved_amount: float
    average_claim_amount: float
    approval_rate: float
    claims_by_status: Dict[str, int]
    claims_by_adjuster: List[Dict[str, Any]]

class ClaimsAnalyticsResponse(BaseModel):
    period: str
    metrics: ClaimsMetrics
    charts: List[ChartData]
    generated_at: datetime

# Financial analytics
class FinancialMetrics(BaseModel):
    total_revenue: float
    total_claims_paid: float
    profit_margin: float
    expense_ratio: float
    revenue_by_product: List[Dict[str, Any]]
    monthly_revenue: List[Dict[str, Any]]

class FinancialAnalyticsResponse(BaseModel):
    period: str
    metrics: FinancialMetrics
    charts: List[ChartData]
    generated_at: datetime

# Performance analytics
class PerformanceMetrics(BaseModel):
    agent_performance: List[Dict[str, Any]]
    adjuster_performance: List[Dict[str, Any]]
    product_performance: List[Dict[str, Any]]
    customer_satisfaction: Optional[float] = None

class PerformanceAnalyticsResponse(BaseModel):
    period: str
    metrics: PerformanceMetrics
    charts: List[ChartData]
    generated_at: datetime

# Dashboard summary
class DashboardSummary(BaseModel):
    active_contracts: int
    pending_claims: int
    total_revenue_mtd: float
    claims_ratio: float
    top_performing_agent: Optional[Dict[str, Any]] = None
    recent_activities: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = [] 