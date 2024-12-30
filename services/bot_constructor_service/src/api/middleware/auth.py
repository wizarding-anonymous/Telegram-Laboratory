from typing import List, Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.integrations import AuthService, get_current_user
from src.config import settings
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AuthMiddleware:
    """
    Middleware for authenticating requests using JWT tokens.
    """

    def __init__(
        self,
        auth_service: AuthService = Depends(),
    ):
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
            credentials: HTTPAuthorizationCredentials = await self.http_bearer(
                request
            )
        except HTTPException:
            logging_client.warning("Authorization header is missing or malformed.")
            raise HTTPException(
                status_code=401, detail="Authorization header is missing or malformed"
            )

        try:
            user = await self.auth_service.get_user_by_token(credentials.credentials)
            request.state.user = user
        except HTTPException as e:
            if e.status_code == 401:
                logging_client.warning("Invalid or expired token")
                raise HTTPException(status_code=401, detail="Invalid or expired token") from e
            logging_client.error(f"Unexpected error during authorization: {e}")
            raise
        except Exception as e:
             logging_client.error(f"Unexpected error during authorization: {e}")
             raise HTTPException(status_code=401, detail="Invalid or expired token") from e


        response = await call_next(request)
        return response


def admin_required(required_roles: Optional[List[str]] = None):
    """
    Dependency to ensure the user has the specified roles.
    If no roles are specified, any authenticated user can access the endpoint.
    """
    logging_client.info(f"Checking if user has required roles: {required_roles}")

    async def check_roles(user: dict = Depends(get_current_user)):
        if required_roles is None:
            logging_client.debug(f"Any user has permission")
            return True
        
        user_roles = user.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            logging_client.warning(
                f"User with id: {user.get('id')} does not have required roles: {required_roles}"
            )
            raise HTTPException(status_code=403, detail=f"Required roles: {required_roles}")

        logging_client.info(f"User with id: {user.get('id')} has required roles: {required_roles}")
        return True
    
    return check_roles