from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils.auth import get_current_user, require_roles
from app.db.database import get_db
from app.db.models import Contract, Client, InsuranceProduct
from app.schemas.contract import (
    ContractCreate, ContractUpdate, Contract as ContractSchema, 
    ContractList, PremiumCalculationParams, PremiumCalculationResult,
    ContractWithDetails
)
from app.functions.contract_service import ContractService

router = APIRouter()

@router.get("/", response_model=ContractList)
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    client_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of contracts"""
    contract_service = ContractService(db)
    contracts, total = contract_service.get_contracts(
        skip=skip, 
        limit=limit, 
        client_id=client_id
    )
    
    return ContractList(
        contracts=contracts,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/calculate", response_model=PremiumCalculationResult)
async def calculate_premium(
    calculation_params: PremiumCalculationParams,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator"))
):
    """Calculate insurance premium"""
    contract_service = ContractService(db)
    
    # Verify product exists
    product = db.query(InsuranceProduct).filter(
        InsuranceProduct.id == calculation_params.product_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found"
        )
    
    result = contract_service.calculate_premium(calculation_params, product)
    return result

@router.post("/", response_model=ContractSchema)
async def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator"))
):
    """Create new insurance contract"""
    contract_service = ContractService(db)
    
    # Verify client exists
    client = db.query(Client).filter(Client.id == contract_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Verify product exists
    product = db.query(InsuranceProduct).filter(
        InsuranceProduct.id == contract_data.product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance product not found"
        )
    
    contract = contract_service.create_contract(
        contract_data, 
        agent_id=current_user.get("user_id")
    )
    return contract

@router.get("/{contract_id}", response_model=ContractWithDetails)
async def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get contract by ID"""
    contract_service = ContractService(db)
    contract = contract_service.get_contract_with_details(contract_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return contract

@router.put("/{contract_id}", response_model=ContractSchema)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "manager", "admin"))
):
    """Update contract information"""
    contract_service = ContractService(db)
    
    # Check if contract exists
    existing_contract = contract_service.get_contract(contract_id)
    if not existing_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    contract = contract_service.update_contract(contract_id, contract_data)
    return contract

@router.post("/{contract_id}/activate")
async def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("manager", "admin"))
):
    """Activate insurance contract"""
    contract_service = ContractService(db)
    
    # Check if contract exists
    existing_contract = contract_service.get_contract(contract_id)
    if not existing_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    success = contract_service.activate_contract(contract_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot activate contract in current state"
        )
    
    return {"message": "Contract activated successfully"} 