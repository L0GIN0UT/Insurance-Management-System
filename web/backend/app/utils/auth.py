import httpx
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings

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
                f"{settings.auth_service_url}/verify-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
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

async def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    """
    Get current user from token
    """
    return await verify_token(credentials)

def require_role(required_role: str):
    """
    Decorator to require specific role
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