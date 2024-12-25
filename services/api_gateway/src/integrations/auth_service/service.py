# services\api_gateway\src\integrations\auth_service\service.py
from typing import Optional, Dict, Any
from dataclasses import dataclass
import structlog

from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ServiceUnavailableError
)
from src.integrations.auth_service.client import AuthServiceClient


logger = structlog.get_logger(__name__)


@dataclass
class TokenPair:
    """Data class for storing access and refresh tokens."""
    access_token: str
    refresh_token: str


class AuthService:
    """Service layer for authentication and authorization operations."""

    def __init__(self, auth_client: AuthServiceClient):
        """Initialize the auth service.
        
        Args:
            auth_client: Client for interacting with auth service
        """
        self._client = auth_client

    async def authenticate_request(
        self,
        authorization_header: Optional[str]
    ) -> Dict[str, Any]:
        """Authenticate request using authorization header.
        
        Args:
            authorization_header: Authorization header from request
                Expected format: "Bearer <token>"

        Returns:
            Dict containing authenticated user information

        Raises:
            AuthenticationError: If authentication fails
            ServiceUnavailableError: If auth service is unavailable
        """
        if not authorization_header:
            raise AuthenticationError("No authorization header provided")

        try:
            scheme, token = authorization_header.split()
        except ValueError:
            raise AuthenticationError("Invalid authorization header format")

        if scheme.lower() != "bearer":
            raise AuthenticationError("Invalid authentication scheme")

        try:
            return await self._client.validate_token(token)
        except AuthenticationError:
            # Try to refresh token if possible
            try:
                new_tokens = await self._client.refresh_token(token)
                return await self._client.validate_token(
                    new_tokens["access_token"]
                )
            except (AuthenticationError, KeyError) as e:
                logger.warning(
                    "Authentication failed",
                    error=str(e),
                    token=token[:10] + "..."
                )
                raise AuthenticationError("Invalid or expired token")

    async def verify_permissions(
        self,
        authorization_header: str,
        required_permissions: list[str]
    ) -> bool:
        """Verify if user has all required permissions.
        
        Args:
            authorization_header: Authorization header from request
            required_permissions: List of required permission strings

        Returns:
            True if user has all required permissions

        Raises:
            AuthenticationError: If authentication fails
            AuthorizationError: If user lacks required permissions
            ServiceUnavailableError: If auth service is unavailable
        """
        if not required_permissions:
            return True

        try:
            scheme, token = authorization_header.split()
        except ValueError:
            raise AuthenticationError("Invalid authorization header format")

        if scheme.lower() != "bearer":
            raise AuthenticationError("Invalid authentication scheme")

        has_permissions = await self._client.verify_permissions(
            token, required_permissions
        )

        if not has_permissions:
            logger.warning(
                "Permission verification failed",
                required_permissions=required_permissions,
                token=token[:10] + "..."
            )
            raise AuthorizationError("Insufficient permissions")

        return True

    async def get_user_profile(
        self,
        user_id: str,
        authorization_header: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user profile information.
        
        Args:
            user_id: ID of the user to get profile for
            authorization_header: Optional authorization header for authenticated requests

        Returns:
            Dict containing user profile information

        Raises:
            AuthenticationError: If user not found or auth fails
            AuthorizationError: If caller lacks permissions
            ServiceUnavailableError: If auth service is unavailable
        """
        token = None
        if authorization_header:
            try:
                scheme, token = authorization_header.split()
                if scheme.lower() != "bearer":
                    token = None
            except ValueError:
                token = None

        try:
            return await self._client.get_user_info(user_id, token)
        except AuthenticationError as e:
            logger.warning(
                "Failed to get user profile",
                error=str(e),
                user_id=user_id
            )
            raise

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token

        Returns:
            TokenPair containing new access and refresh tokens

        Raises:
            AuthenticationError: If refresh token is invalid
            ServiceUnavailableError: If auth service is unavailable
        """
        try:
            tokens = await self._client.refresh_token(refresh_token)
            return TokenPair(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"]
            )
        except (KeyError, AuthenticationError) as e:
            logger.warning(
                "Token refresh failed",
                error=str(e),
                refresh_token=refresh_token[:10] + "..."
            )
            raise AuthenticationError("Invalid refresh token")

    async def validate_service_token(
        self,
        service_token: str
    ) -> Dict[str, Any]:
        """Validate service-to-service authentication token.
        
        Args:
            service_token: JWT token for service authentication

        Returns:
            Dict containing service information

        Raises:
            AuthenticationError: If token is invalid
            ServiceUnavailableError: If auth service is unavailable
        """
        try:
            return await self._client.validate_token(service_token)
        except AuthenticationError as e:
            logger.warning(
                "Service token validation failed",
                error=str(e),
                token=service_token[:10] + "..."
            )
            raise AuthenticationError("Invalid service token")