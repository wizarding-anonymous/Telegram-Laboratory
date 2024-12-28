from typing import List, Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.integrations.auth_service import AuthService, get_current_user
from src.config import settings
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AuthMiddleware:
    """
    Middleware for authenticating requests using JWT tokens.
    """
    def __init__(self, auth_service: AuthService = Depends(),):
        self.auth_service = auth_service
        self.http_bearer = HTTPBearer()
        logging_client.info("AuthMiddleware initialized")

    async def __call__(self, request: Request, call_next):
        """
        Authenticates the user based on the JWT token in the Authorization header.
        """
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)  # Skip authentication for health and metrics endpoints

        try:
             credentials: HTTPAuthorizationCredentials = await self.http_bearer(request)
        except HTTPException:
            logging_client.warning("Authorization header is missing or malformed.")
            raise HTTPException(status_code=401, detail="Authorization header is missing or malformed")

        try:
            await self.auth_service.get_user_by_token(credentials.credentials)
        except HTTPException as e:
            if e.status_code == 401:
                logging_client.warning("Invalid or expired token")
                raise HTTPException(status_code=401, detail="Invalid or expired token") from e
            logging_client.error(f"Unexpected error during authorization: {e}")
            raise

        response = await call_next(request)
        return response


def admin_required():
    """
    Dependency to ensure the user has the "admin" role.
    """
    logging_client.info("Checking if user has admin rights")

    async def check_admin(user: dict = Depends(get_current_user)):
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user.get('id')} has not admin rights")
            raise HTTPException(status_code=403, detail="Admin role required")
        logging_client.info(f"User with id: {user.get('id')} has admin rights")
        return True
    return check_admin