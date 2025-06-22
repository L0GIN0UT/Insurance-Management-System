from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from app.utils.auth import get_current_user, require_roles
import httpx
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str

class UserRoleUpdate(BaseModel):
    role: str

@router.get("/")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_roles("admin"))
):
    """Get list of users (admin only)"""
    
    try:
        # Forward request to auth service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.auth_service_url}/users",
                params={"skip": skip, "limit": limit},
                headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch users"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )

@router.post("/")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_roles("admin"))
):
    """Create new user (admin only)"""
    
    # Validate role
    valid_roles = ["agent", "adjuster", "operator", "manager", "admin"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        # Forward request to auth service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/register",
                json=user_data.dict(),
                headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to create user"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    current_user: dict = Depends(require_roles("admin"))
):
    """Update user role (admin only)"""
    
    # Validate role
    valid_roles = ["agent", "adjuster", "operator", "manager", "admin"]
    if role_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        # Forward request to auth service
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{settings.auth_service_url}/users/{user_id}/role",
                json=role_data.dict(),
                headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to update user role"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user role"
        )

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: dict = Depends(require_roles("admin"))
):
    """Get user by ID (admin only)"""
    
    try:
        # Forward request to auth service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.auth_service_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="User not found"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user"
        ) 