from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date

class FinanceReportData(BaseModel):
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    total_premiums_collected: float
    total_claims_paid: float
    net_profit: float
    outstanding_premiums: float
    pending_claims_amount: float
    monthly_breakdown: List[Dict[str, Any]]
    top_performing_agents: List[Dict[str, Any]]
    contract_types_revenue: Dict[str, float]

class ActivityReportData(BaseModel):
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    new_clients: int
    new_contracts: int
    claims_processed: int
    contracts_expired: int
    active_agents: int
    daily_activity: List[Dict[str, Any]]
    agent_performance: List[Dict[str, Any]]
    contract_status_distribution: Dict[str, int]
    claim_processing_times: Dict[str, float]

class AgentPerformance(BaseModel):
    agent_id: int
    agent_name: str
    contracts_created: int
    total_premiums: float
    clients_acquired: int
    conversion_rate: float

class MonthlyBreakdown(BaseModel):
    month: str
    premiums: float
    claims: float
    profit: float
    contracts_count: int 