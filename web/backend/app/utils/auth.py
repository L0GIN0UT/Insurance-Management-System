import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings
from typing import List, Union

security = HTTPBearer()
settings = get_settings()

async def verify_token(credentials: HTTPAuthorizationCredentials):
    """
    Verify JWT token with auth service
    """
    token = credentials.credentials
    
    try:
        # Send request to auth service to verify token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/auth/verify-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"DEBUG: Auth service response. Status: {response.status_code}, Response: {response.text}")
            
            if response.status_code != 200:
                print(f"DEBUG: Auth verification failed: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Auth service returned {response.status_code}: {response.text}"
            )
            
            if response.status_code == 200:
                user_data = response.json()
                user_data['token'] = token  # Store token for forwarding
                return user_data
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user from token
    """
    return await verify_token(credentials)

def require_roles(*allowed_roles: str):
    """
    Dependency to require specific roles
    Usage: @router.get("/", dependencies=[Depends(require_roles("admin", "manager"))])
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {' or '.join(allowed_roles)}. Your role: {user_role}"
            )
        return current_user
    return role_checker

def require_role(required_role: str):
    """
    Decorator to require specific role (legacy, prefer require_roles)
    """
    def role_checker(user_data: dict):
        user_role = user_data.get("role")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}"
            )
        return user_data
    return role_checker 