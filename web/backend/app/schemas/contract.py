from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PremiumCalculationParams(BaseModel):
    product_id: int
    coverage_amount: float
    client_age: Optional[int] = None
    risk_factors: dict = {}
    duration_months: int = 12

class PremiumCalculationResult(BaseModel):
    base_premium: float
    risk_multiplier: float
    final_premium: float
    monthly_premium: float
    calculation_details: dict

class ContractBase(BaseModel):
    client_id: int
    product_id: int
    premium_amount: float
    coverage_amount: float
    start_date: date
    end_date: date
    terms_conditions: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    premium_amount: Optional[float] = None
    coverage_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ContractStatus] = None
    terms_conditions: Optional[str] = None

class Contract(ContractBase):
    id: int
    contract_number: str
    agent_id: int
    status: ContractStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContractWithDetails(Contract):
    client_name: Optional[str] = None
    product_name: Optional[str] = None
    agent_name: Optional[str] = None

class ContractList(BaseModel):
    contracts: list[ContractWithDetails]
    total: int
    skip: int
    limit: int 