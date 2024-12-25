# services\api_gateway\src\integrations\auth_service\client.py
from typing import Optional, Dict, Any
from http import HTTPStatus

import structlog
from aiohttp import ClientSession, ClientError

from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ServiceUnavailableError
)
from src.core.settings import settings


logger = structlog.get_logger(__name__)


class AuthServiceClient:
    """Client for interacting with the Authentication Service."""

    def __init__(self, session: ClientSession):
        """Initialize the auth service client.
        
        Args:
            session: aiohttp client session for making HTTP requests
        """
        self._session = session
        self._base_url = f"{settings.auth_service_url}/api/v1"

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate access token and get user info.
        
        Args:
            token: JWT access token to validate

        Returns:
            Dict containing user information if token is valid

        Raises:
            AuthenticationError: If token is invalid or expired
            AuthorizationError: If user lacks required permissions
            ServiceUnavailableError: If auth service is unavailable
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            async with self._session.get(
                f"{self._base_url}/auth/validate",
                headers=headers
            ) as response:
                if response.status == HTTPStatus.OK:
                    return await response.json()
                
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise AuthenticationError("Invalid or expired token")
                
                if response.status == HTTPStatus.FORBIDDEN:
                    raise AuthorizationError("Insufficient permissions")
                
                raise ServiceUnavailableError(
                    f"Auth service returned unexpected status: {response.status}"
                )

        except ClientError as e:
            logger.error("Error validating token", error=str(e))
            raise ServiceUnavailableError("Auth service is unavailable")

    async def refresh_token(
        self,
        refresh_token: str
    ) -> Dict[str, Any]:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token

        Returns:
            Dict containing new access and refresh tokens

        Raises:
            AuthenticationError: If refresh token is invalid
            ServiceUnavailableError: If auth service is unavailable
        """
        try:
            headers = {"Authorization": f"Bearer {refresh_token}"}
            async with self._session.post(
                f"{self._base_url}/auth/refresh",
                headers=headers
            ) as response:
                if response.status == HTTPStatus.OK:
                    return await response.json()
                
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise AuthenticationError("Invalid refresh token")
                
                raise ServiceUnavailableError(
                    f"Auth service returned unexpected status: {response.status}"
                )

        except ClientError as e:
            logger.error("Error refreshing token", error=str(e))
            raise ServiceUnavailableError("Auth service is unavailable")

    async def verify_permissions(
        self,
        token: str,
        required_permissions: list[str]
    ) -> bool:
        """Verify if user has required permissions.
        
        Args:
            token: JWT access token
            required_permissions: List of required permission strings

        Returns:
            True if user has all required permissions, False otherwise

        Raises:
            AuthenticationError: If token is invalid
            ServiceUnavailableError: If auth service is unavailable
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"permissions": required_permissions}
            
            async with self._session.get(
                f"{self._base_url}/auth/verify-permissions",
                headers=headers,
                params=params
            ) as response:
                if response.status == HTTPStatus.OK:
                    result = await response.json()
                    return result.get("has_permissions", False)
                
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise AuthenticationError("Invalid token")
                
                raise ServiceUnavailableError(
                    f"Auth service returned unexpected status: {response.status}"
                )

        except ClientError as e:
            logger.error(
                "Error verifying permissions",
                error=str(e),
                permissions=required_permissions
            )
            raise ServiceUnavailableError("Auth service is unavailable")

    async def get_user_info(
        self,
        user_id: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed user information.
        
        Args:
            user_id: ID of the user to get info for
            token: Optional JWT token for authorization

        Returns:
            Dict containing user information

        Raises:
            AuthenticationError: If token is invalid
            AuthorizationError: If caller lacks permissions
            ServiceUnavailableError: If auth service is unavailable
        """
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            async with self._session.get(
                f"{self._base_url}/users/{user_id}",
                headers=headers
            ) as response:
                if response.status == HTTPStatus.OK:
                    return await response.json()
                
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise AuthenticationError("Invalid token")
                
                if response.status == HTTPStatus.FORBIDDEN:
                    raise AuthorizationError(
                        "Insufficient permissions to access user info"
                    )
                
                if response.status == HTTPStatus.NOT_FOUND:
                    raise AuthenticationError(f"User {user_id} not found")
                
                raise ServiceUnavailableError(
                    f"Auth service returned unexpected status: {response.status}"
                )

        except ClientError as e:
            logger.error("Error getting user info", error=str(e), user_id=user_id)
            raise ServiceUnavailableError("Auth service is unavailable")