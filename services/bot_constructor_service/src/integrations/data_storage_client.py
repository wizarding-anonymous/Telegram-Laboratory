import httpx
from typing import Dict, Any, Optional
from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class DataStorageClient:
    """
    Client for interacting with the Data Storage Service.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.DATA_STORAGE_SERVICE_URL
        if not self.base_url:
             raise ValueError("Data storage service URL is not configured")

    @handle_exceptions
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Sends a request to the Data Storage Service.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): API endpoint in Data Storage Service.
            data (Optional[Dict[str, Any]]): Request body.
            params (Optional[Dict[str, Any]]): Query parameters
            headers (Optional[Dict[str, str]]): Request headers

        Returns:
            Dict[str, Any]: Response data from Data Storage Service.
        """
        url = f"{self.base_url}{endpoint}"
        
        headers = headers or {}
        headers.update({'Content-Type': 'application/json'})

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers = headers,
                timeout=10
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()

    @handle_exceptions
    async def create_database_for_bot(self, bot_id: int, user_id: int) -> Dict[str, Any]:
        """
        Creates a new database for a bot.

        Args:
            bot_id (int): The ID of the bot.
            user_id (int): The ID of the user that owns the bot

        Returns:
            Dict[str, Any]: Response from Data Storage Service.
        """
        return await self.request(
            method="POST", endpoint="/databases/", data={"bot_id": bot_id, "user_id": user_id}
        )

    @handle_exceptions
    async def get_bot_database_dsn(self, bot_id: int) -> Dict[str, Any]:
        """
        Retrieves the database DSN for a bot.

        Args:
            bot_id (int): The ID of the bot.

        Returns:
            Dict[str, Any]: Response from Data Storage Service containing the DSN.
        """
        return await self.request(method="GET", endpoint=f"/meta/bots/{bot_id}")

    @handle_exceptions
    async def delete_database_for_bot(self, bot_id: int) -> Dict[str, Any]:
        """
         Deletes a database for a bot.

        Args:
            bot_id (int): The ID of the bot.

        Returns:
            Dict[str, Any]: Response from Data Storage Service.
        """
        return await self.request(method="DELETE", endpoint=f"/databases/{bot_id}")

    @handle_exceptions
    async def apply_migrations_for_bot_database(self, bot_id: int) -> Dict[str,Any]:
          """
           Applies migrations to bot database

          Args:
              bot_id (int): The ID of the bot.

          Returns:
              Dict[str, Any]: Response from Data Storage Service.
          """
          return await self.request(method="POST", endpoint=f"/databases/{bot_id}/migrate")