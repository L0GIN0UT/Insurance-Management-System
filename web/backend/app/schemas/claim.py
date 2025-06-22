from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class ClaimDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_INVESTIGATION = "requires_investigation"

class ClaimBase(BaseModel):
    contract_id: int
    incident_date: date
    description: str
    claimed_amount: Optional[float] = None

class ClaimCreate(ClaimBase):
    pass

class ClaimUpdate(BaseModel):
    description: Optional[str] = None
    claimed_amount: Optional[float] = None
    status: Optional[ClaimStatus] = None
    adjuster_notes: Optional[str] = None

class ClaimDecisionRequest(BaseModel):
    decision: ClaimDecision
    approved_amount: Optional[float] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None

class Claim(ClaimBase):
    id: int
    claim_number: str
    reported_date: date
    approved_amount: Optional[float] = None
    status: ClaimStatus
    adjuster_id: Optional[int] = None
    adjuster_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClaimWithDetails(Claim):
    contract_number: Optional[str] = None
    client_name: Optional[str] = None
    adjuster_name: Optional[str] = None

class ClaimList(BaseModel):
    claims: list[ClaimWithDetails]
    total: int
    skip: int
    limit: int

class PendingClaimsList(BaseModel):
    pending_claims: list[ClaimWithDetails]
    total: int
    skip: int
    limit: int 