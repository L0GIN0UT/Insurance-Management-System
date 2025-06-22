from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils.auth import get_current_user, require_roles
from app.db.database import get_db
from app.db.models import Client
from app.schemas.client import ClientCreate, ClientUpdate, Client as ClientSchema, ClientList
from app.functions.client_service import ClientService

router = APIRouter()

@router.get("/", response_model=ClientList)
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator", "admin"))
):
    """Get list of clients"""
    client_service = ClientService(db)
    clients, total = client_service.get_clients(skip=skip, limit=limit)
    
    return ClientList(
        clients=clients,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=ClientSchema)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator", "admin"))
):
    """Create new client"""
    client_service = ClientService(db)
    
    # Check if client with this email already exists
    existing_client = client_service.get_client_by_email(client_data.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )
    
    client = client_service.create_client(client_data, created_by=current_user.get("user_id"))
    return client

@router.get("/{client_id}", response_model=ClientSchema)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator", "admin"))
):
    """Get client by ID"""
    client_service = ClientService(db)
    client = client_service.get_client(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client

@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("agent", "operator", "admin"))
):
    """Update client information"""
    client_service = ClientService(db)
    
    # Check if client exists
    existing_client = client_service.get_client(client_id)
    if not existing_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check email uniqueness if email is being updated
    if client_data.email and client_data.email != existing_client.email:
        email_client = client_service.get_client_by_email(client_data.email)
        if email_client and email_client.id != client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists"
            )
    
    client = client_service.update_client(client_id, client_data)
    return client

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin"))
):
    """Delete client (admin only)"""
    client_service = ClientService(db)
    
    # Check if client exists
    existing_client = client_service.get_client(client_id)
    if not existing_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check if client has active contracts
    if client_service.has_active_contracts(client_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete client with active contracts"
        )
    
    client_service.delete_client(client_id)
    return {"message": "Client deleted successfully"} 