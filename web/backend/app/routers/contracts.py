from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    client_id: int = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of contracts"""
    # TODO: Implement database logic
    return {
        "contracts": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
        "filters": {"client_id": client_id}
    }

@router.post("/")
async def create_contract(
    # contract_data: ContractCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new insurance contract"""
    # Only agents and managers can create contracts
    allowed_roles = ["agent", "manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents and managers can create contracts"
        )
    
    # TODO: Implement contract creation logic
    return {"message": "Contract created successfully"}

@router.get("/{contract_id}")
async def get_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get contract by ID"""
    # TODO: Implement get contract logic
    return {"contract_id": contract_id, "data": {}}

@router.put("/{contract_id}")
async def update_contract(
    contract_id: int,
    # contract_data: ContractUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update contract information"""
    allowed_roles = ["agent", "manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # TODO: Implement contract update logic
    return {"message": "Contract updated successfully"}

@router.post("/{contract_id}/calculate-premium")
async def calculate_premium(
    contract_id: int,
    # calculation_params: PremiumCalculationParams,
    current_user: dict = Depends(get_current_user)
):
    """Calculate insurance premium for contract"""
    allowed_roles = ["agent", "manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # TODO: Implement premium calculation logic
    return {"premium": 0, "calculation_details": {}}

@router.post("/{contract_id}/activate")
async def activate_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Activate insurance contract"""
    allowed_roles = ["manager", "admin"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can activate contracts"
        )
    
    # TODO: Implement contract activation logic
    return {"message": "Contract activated successfully"} 