from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    identification_number: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    identification_number: Optional[str] = None

class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

class ClientList(BaseModel):
    clients: list[Client]
    total: int
    skip: int
    limit: int 