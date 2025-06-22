from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date

class FinanceReportData(BaseModel):
    total_premiums: float
    total_claims: float
    profit: float
    period: Dict[str, str]
    by_month: List[Dict[str, Any]]
    by_product: List[Dict[str, Any]]

class ActivityReportData(BaseModel):
    total_users: int
    active_users: int
    by_role: List[Dict[str, Any]]
    top_agents: List[Dict[str, Any]]

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

class AdminRoleData(BaseModel):
    roles: List[Dict[str, Any]]
    users_by_role: Dict[str, int]
    recent_role_changes: List[Dict[str, Any]]

class AdminAuditData(BaseModel):
    logs: List[Dict[str, Any]]
    total_logs: int
    filtered_count: int
    summary: Dict[str, Any] 