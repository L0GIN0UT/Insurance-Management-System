from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.utils.auth import get_current_user, require_roles
from app.db.database import get_db
from app.schemas.claim import (
    ClaimCreate, ClaimUpdate, Claim as ClaimSchema, 
    ClaimList, ClaimDecisionRequest, PendingClaimsList,
    ClaimWithDetails
)
from app.functions.claim_service import ClaimService

router = APIRouter()

class ClaimCreate(BaseModel):
    contract_id: int
    incident_date: str
    description: str
    claim_amount: float
    documents: List[str] = []

class ClaimSubmitRequest(BaseModel):
    contract_id: int
    incident_date: str
    description: str
    claim_amount: float
    documents: List[str] = []
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    customer_contact: str = None
    witnesses: List[str] = []
    
class ClaimSubmitResponse(BaseModel):
    claim_id: int
    claim_number: str
    status: str
    estimated_processing_time: str
    adjuster_assigned: bool
    validation_checklist: dict

class ClaimDecision(BaseModel):
    decision: str  # "approved", "rejected", "requires_investigation"
    approved_amount: float = None
    rejection_reason: str = None
    notes: str = None

@router.get("/", response_model=ClaimList)
async def get_claims(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    contract_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of insurance claims"""
    claim_service = ClaimService(db)
    claims, total = claim_service.get_claims(
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        contract_id=contract_id
    )
    
    return ClaimList(
        claims=claims,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/pending", response_model=PendingClaimsList)
async def get_pending_claims(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("adjuster"))
):
    """Get pending claims for adjustment"""
    claim_service = ClaimService(db)
    pending_claims, total = claim_service.get_pending_claims(skip=skip, limit=limit)
    
    return PendingClaimsList(
        pending_claims=pending_claims,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=ClaimSchema)
async def create_claim(
    claim_data: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator", "admin"))
):
    """Create new insurance claim"""
    claim_service = ClaimService(db)
    claim = claim_service.create_claim(claim_data, created_by=current_user.get("user_id"))
    return claim

@router.get("/{claim_id}", response_model=ClaimWithDetails)
async def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get claim by ID"""
    claim_service = ClaimService(db)
    claim = claim_service.get_claim_with_details(claim_id)
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    return claim

@router.put("/{claim_id}/decision", response_model=ClaimSchema)
async def make_claim_decision(
    claim_id: int,
    decision_data: ClaimDecisionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("adjuster"))
):
    """Make decision on insurance claim (adjuster only)"""
    claim_service = ClaimService(db)
    
    # Check if claim exists
    existing_claim = claim_service.get_claim(claim_id)
    if not existing_claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    claim = claim_service.make_decision(
        claim_id, 
        decision_data, 
        adjuster_id=current_user.get("user_id")
    )
    
    return claim

@router.put("/{claim_id}", response_model=ClaimSchema)
async def update_claim(
    claim_id: int,
    claim_data: ClaimUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("adjuster", "manager", "admin"))
):
    """Update claim information"""
    claim_service = ClaimService(db)
    
    # Check if claim exists
    existing_claim = claim_service.get_claim(claim_id)
    if not existing_claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    claim = claim_service.update_claim(claim_id, claim_data)
    return claim

@router.post("/{claim_id}/process")
async def process_claim(
    claim_id: int,
    # processing_data: ClaimProcessingData,
    current_user: dict = Depends(get_current_user)
):
    """Process insurance claim (adjuster only)"""
    if current_user.get("role") != "adjuster":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only adjusters can process claims"
        )
    
    # TODO: Implement claim processing logic
    return {"message": "Claim processed successfully"}

@router.post("/{claim_id}/approve")
async def approve_claim(
    claim_id: int,
    approval_amount: float,
    current_user: dict = Depends(get_current_user)
):
    """Approve insurance claim (manager only)"""
    allowed_roles = ["manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can approve claims"
        )
    
    # TODO: Implement claim approval logic
    return {"message": "Claim approved successfully", "amount": approval_amount}

@router.post("/{claim_id}/reject")
async def reject_claim(
    claim_id: int,
    rejection_reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Reject insurance claim"""
    allowed_roles = ["adjuster", "manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # TODO: Implement claim rejection logic
    return {"message": "Claim rejected", "reason": rejection_reason} 

@router.post("/submit", response_model=ClaimSubmitResponse)
async def submit_claim_to_adjuster(
    claim_data: ClaimSubmitRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("operator"))
):
    """Submit claim to adjuster with validation checklist (operator only)"""
    claim_service = ClaimService(db)
    
    # Проверяем существование договора
    from app.db.models import Contract
    contract = db.query(Contract).filter(Contract.id == claim_data.contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Проверяем активность договора
    if contract.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract is not active"
        )
    
    # Валидационный чек-лист
    validation_checklist = {
        "contract_valid": True,
        "contract_active": contract.status == "active",
        "incident_date_valid": True,  # TODO: проверить что дата не в будущем
        "description_complete": len(claim_data.description) >= 20,
        "amount_reasonable": claim_data.claim_amount <= contract.coverage_amount,
        "documents_attached": len(claim_data.documents) > 0,
        "contact_provided": claim_data.customer_contact is not None
    }
    
    # Все проверки должны быть пройдены
    all_valid = all(validation_checklist.values())
    if not all_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Validation failed",
                "checklist": validation_checklist
            }
        )
    
    # Создаем заявку
    create_data = ClaimCreate(
        contract_id=claim_data.contract_id,
        incident_date=claim_data.incident_date,
        description=claim_data.description,
        claim_amount=claim_data.claim_amount,
        documents=claim_data.documents
    )
    
    claim = claim_service.create_claim(create_data, created_by=current_user.get("user_id"))
    
    # Назначаем урегулировщика (простая логика)
    # TODO: Реализовать умное назначение по загрузке
    adjuster_assigned = True
    
    # Оценка времени обработки
    if claim_data.priority == "urgent":
        processing_time = "1-2 дня"
    elif claim_data.priority == "high":
        processing_time = "3-5 дней"
    else:
        processing_time = "5-10 дней"
    
    return ClaimSubmitResponse(
        claim_id=claim.id,
        claim_number=claim.claim_number,
        status=claim.status,
        estimated_processing_time=processing_time,
        adjuster_assigned=adjuster_assigned,
        validation_checklist=validation_checklist
    ) 