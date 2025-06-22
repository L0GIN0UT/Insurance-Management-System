from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from ..db.models import ContractStatus

# Base Contract schema
class ContractBase(BaseModel):
    contract_number: str
    client_id: int
    product_id: int
    agent_id: int
    premium_amount: float
    coverage_amount: float
    start_date: date
    end_date: date
    status: ContractStatus = ContractStatus.DRAFT
    terms_conditions: Optional[str] = None

# Schema for creating a contract
class ContractCreate(ContractBase):
    @validator('premium_amount', 'coverage_amount')
    def validate_amounts(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

# Schema for updating a contract
class ContractUpdate(BaseModel):
    premium_amount: Optional[float] = None
    coverage_amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ContractStatus] = None
    terms_conditions: Optional[str] = None

# Schema for contract response
class Contract(ContractBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema for contract list with pagination
class ContractList(BaseModel):
    contracts: List[Contract]
    total: int
    skip: int
    limit: int

# Schema for contract with relationships
class ContractWithDetails(Contract):
    client: Optional['ClientBase'] = None
    product: Optional['ProductBase'] = None
    claims: List['ClaimBase'] = []
    
    class Config:
        from_attributes = True

# Schema for premium calculation
class PremiumCalculationParams(BaseModel):
    base_premium: float
    coverage_amount: float
    risk_factors: dict = {}
    discounts: dict = {}

class PremiumCalculationResult(BaseModel):
    base_premium: float
    total_premium: float
    risk_adjustments: dict
    discounts_applied: dict
    calculation_details: dict

# Forward reference resolution will be done at the end of all modules 