# services\bot_constructor_service\src\integrations\auth_service.py
import httpx
from loguru import logger
from fastapi import HTTPException
import os


class AuthService:
    """
    Client for interacting with the Auth Service.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize the AuthService client.

        Args:
            base_url (str): Base URL of the Auth Service API. Defaults to AUTH_SERVICE_URL environment variable.
        """
        self.base_url = base_url or os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
        if not self.base_url:
            raise ValueError("Auth Service URL is required")
        logger.info(f"AuthService initialized with base URL: {self.base_url}")

    async def validate_user_permissions(self, user_id: int, permission: str) -> bool:
        """
        Validate if a user has the required permission.

        Args:
            user_id (int): ID of the user to validate.
            permission (str): The required permission to check.

        Returns:
            bool: True if the user has the required permission.

        Raises:
            HTTPException: If the user does not have the required permission or the request fails.
        """
        url = f"{self.base_url}/permissions/validate"
        payload = {"user_id": user_id, "permission": permission}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to validate permissions: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Permission validation failed: {response.text}",
                )
            data = response.json()
            if not data.get("has_permission"):
                logger.warning(f"User {user_id} lacks permission: {permission}")
                raise HTTPException(
                    status_code=403,
                    detail=f"User does not have the required permission: {permission}",
                )
            logger.info(f"User {user_id} has the required permission: {permission}")
            return True

    async def get_user_details(self, token: str) -> dict:
        """
        Retrieve user details using the provided token.

        Args:
            token (str): JWT token of the user.

        Returns:
            dict: User details as returned by the Auth Service.

        Raises:
            HTTPException: If the token is invalid or the request fails.
        """
        url = f"{self.base_url}/users/me"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to retrieve user details: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to retrieve user details: {response.text}",
                )
            user_data = response.json()
            logger.info(f"User details retrieved: {user_data}")
            return user_data

    async def check_health(self) -> bool:
        """
        Check the health of the Auth Service.

        Returns:
            bool: True if the Auth Service is healthy, False otherwise.
        """
        url = f"{self.base_url}/health"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    logger.info("Auth Service is healthy")
                    return True
                else:
                    logger.warning(f"Auth Service health check failed: {response.text}")
                    return False
            except httpx.RequestError as exc:
                logger.error(f"Error checking Auth Service health: {exc}")
                return False
