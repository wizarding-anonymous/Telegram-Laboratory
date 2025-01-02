from typing import Dict, Optional
import httpx
from fastapi import HTTPException, status
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AuthService:
    """
    Client for interacting with the Auth Service.
    """

    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL

    @handle_exceptions
    async def get_user_by_token(self, token: str) -> Optional[Dict]:
        """
        Sends a request to the Auth Service to validate the JWT token and retrieve user information.
        """
        logger.debug(f"Sending request to Auth Service to get user by token: {token}")
        logging_client.debug(f"Sending request to Auth Service to get user by token: {token}")
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = await client.get(
                    url=f"{self.base_url}/auth/me", headers=headers, timeout=10
                )
                response.raise_for_status()
                user_data = response.json()
                logger.debug(f"Successfully retrieved user data from Auth Service: {user_data}")
                logging_client.debug(f"Successfully retrieved user data from Auth Service: {user_data}")
                return user_data
            except httpx.HTTPError as e:
                if e.response is not None and e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                    logger.warning(f"Unauthorized access, invalid or expired token. {e}")
                    logging_client.warning(f"Unauthorized access, invalid or expired token. {e}")
                    return None
                else:
                     logger.error(f"Error communicating with Auth Service: {e}")
                     logging_client.error(f"Error communicating with Auth Service: {e}")
                     raise HTTPException(
                         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error communicating with Auth Service: {e}"
                   ) from e
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                logging_client.error(f"An unexpected error occurred: {e}")
                raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Unexpected error: {e}"
                    ) from e