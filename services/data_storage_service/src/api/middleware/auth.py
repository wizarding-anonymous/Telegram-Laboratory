from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

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
        Validates the token and retrieves user information.
        """
        logger.info("Authenticating user...")
        if not credentials:
            logger.warning("Authorization header is missing.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is missing",
            )
        
        token = credentials.credentials
        logger.debug(f"Extracted token: {token}")
        
        try:
          user = await self.auth_service.get_user_by_token(token)
          if not user:
              logger.warning("Invalid or expired token.")
              raise HTTPException(
                  status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="Invalid or expired token",
              )
          logger.info(f"User authenticated successfully. User: {user}")
          return user
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            raise


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
        logger.info(f"Checking if user has admin role. User: {user}")
        if "admin" not in user.get("roles", []):
            logger.warning(f"User does not have admin role. User roles: {user.get('roles', [])}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required for this endpoint",
            )
        logger.info("User has admin role.")
        return user
    return admin_dependency