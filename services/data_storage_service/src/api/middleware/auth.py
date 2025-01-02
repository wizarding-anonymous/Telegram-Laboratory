from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.integrations.auth_service import AuthService
from src.core.utils import handle_exceptions


class AuthMiddleware:
    def __init__(self, auth_service: AuthService = Depends(AuthService)):
        self.auth_service = auth_service
        self.security = HTTPBearer()

    @handle_exceptions
    async def __call__(
        self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())
    ):
        """
        Middleware to authenticate and authorize users using JWT tokens.
        Validates the token and checks user roles.
        """

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is missing",
            )
        
        token = credentials.credentials
        user = await self.auth_service.get_user_by_token(token)
        
        if not user:
             raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail="Invalid or expired token",
            )

        return user


def auth_required():
    """
    Dependency to enforce authentication for a given endpoint.
    """
    async def auth_dependency(user: dict = Depends(AuthMiddleware())):
       return user
    
    return auth_dependency


def admin_required():
    """
    Dependency to enforce admin role for a given endpoint.
    """
    async def admin_dependency(user: dict = Depends(AuthMiddleware())):
        if "admin" not in user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for this endpoint",
            )
        return user
    return admin_dependency