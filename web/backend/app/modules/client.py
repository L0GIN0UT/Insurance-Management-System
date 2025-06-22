from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime

# Base Client schema
class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    identification_number: Optional[str] = None

# Schema for creating a client
class ClientCreate(ClientBase):
    first_name: str
    last_name: str
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

# Schema for updating a client
class ClientUpdate(ClientBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Schema for client response
class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Schema for client list with pagination
class ClientList(BaseModel):
    clients: List[Client]
    total: int
    skip: int
    limit: int

# Schema for client with contracts
class ClientWithContracts(Client):
    contracts: List['ContractBase'] = []
    
    class Config:
        from_attributes = True

# Forward reference resolution
from .contract import ContractBase
ClientWithContracts.model_rebuild() 