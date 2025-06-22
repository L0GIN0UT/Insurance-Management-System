from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_claims(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    contract_id: int = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of insurance claims"""
    # TODO: Implement database logic
    return {
        "claims": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "filters": {"status": status_filter, "contract_id": contract_id}
    }

@router.post("/")
async def create_claim(
    # claim_data: ClaimCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new insurance claim"""
    # Agents, operators, and managers can create claims
    allowed_roles = ["agent", "operator", "manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create claims"
        )
    
    # TODO: Implement claim creation logic
    return {"message": "Claim created successfully", "claim_id": 1}

@router.get("/{claim_id}")
async def get_claim(
    claim_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get claim by ID"""
    # TODO: Implement get claim logic
    return {"claim_id": claim_id, "data": {}}

@router.put("/{claim_id}")
async def update_claim(
    claim_id: int,
    # claim_data: ClaimUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update claim information"""
    allowed_roles = ["adjuster", "manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only adjusters and managers can update claims"
        )
    
    # TODO: Implement claim update logic
    return {"message": "Claim updated successfully"}

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