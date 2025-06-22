from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    AGENT = "agent"
    ADJUSTER = "adjuster"
    OPERATOR = "operator"
    MANAGER = "manager"
    ADMIN = "admin"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None

class UserRoleUpdate(BaseModel):
    role: UserRole

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: list[User]
    total: int
    skip: int
    limit: int 