from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, datetime
from ..db.models import ClaimStatus

# Base Claim schema
class ClaimBase(BaseModel):
    claim_number: str
    contract_id: int
    incident_date: date
    reported_date: Optional[date] = None
    description: str
    claimed_amount: Optional[float] = None
    approved_amount: Optional[float] = None
    status: ClaimStatus = ClaimStatus.SUBMITTED
    adjuster_id: Optional[int] = None
    adjuster_notes: Optional[str] = None

# Schema for creating a claim
class ClaimCreate(ClaimBase):
    description: str
    incident_date: date
    
    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @validator('claimed_amount')
    def validate_claimed_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Claimed amount must be positive')
        return v
    
    @validator('incident_date')
    def validate_incident_date(cls, v):
        if v > date.today():
            raise ValueError('Incident date cannot be in the future')
        return v

# Schema for updating a claim
class ClaimUpdate(BaseModel):
    description: Optional[str] = None
    claimed_amount: Optional[float] = None
    approved_amount: Optional[float] = None
    status: Optional[ClaimStatus] = None
    adjuster_id: Optional[int] = None
    adjuster_notes: Optional[str] = None

# Schema for claim response
class Claim(ClaimBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema for claim list with pagination
class ClaimList(BaseModel):
    claims: List[Claim]
    total: int
    skip: int
    limit: int

# Schema for claim with contract details
class ClaimWithDetails(Claim):
    contract: Optional['ContractBase'] = None
    
    class Config:
        from_attributes = True

# Schema for claim processing
class ClaimProcessingData(BaseModel):
    adjuster_notes: str
    approved_amount: Optional[float] = None
    status: ClaimStatus
    
    @validator('approved_amount')
    def validate_approved_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Approved amount cannot be negative')
        return v

# Schema for claim approval
class ClaimApproval(BaseModel):
    approved_amount: float
    approval_notes: Optional[str] = None
    
    @validator('approved_amount')
    def validate_approved_amount(cls, v):
        if v <= 0:
            raise ValueError('Approved amount must be positive')
        return v

# Schema for claim rejection
class ClaimRejection(BaseModel):
    rejection_reason: str
    rejection_notes: Optional[str] = None
    
    @validator('rejection_reason')
    def validate_rejection_reason(cls, v):
        if not v.strip():
            raise ValueError('Rejection reason cannot be empty')
        return v.strip() 