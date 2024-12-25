# services\api_gateway\src\integrations\bot_constructor\client.py
from typing import Optional, List, Dict, Any
import aiohttp
from aiohttp import ClientSession
from src.core.abstractions.integrations import BaseIntegrationClient
from src.core.config import Settings
from src.core.exceptions import (
    IntegrationError,
    BotNotFoundError,
    BotValidationError,
    BotCreationError
)
from src.integrations.bot_constructor.schemas import (
    Bot,
    BotCreate,
    BotUpdate,
    BotResponse,
    BotList
)


class BotConstructorClient(BaseIntegrationClient):
    """Client for interacting with Bot Constructor service."""
    
    def __init__(self, settings: Settings, session: Optional[ClientSession] = None):
        """Initialize Bot Constructor client.
        
        Args:
            settings: Application settings
            session: Optional aiohttp ClientSession
        """
        super().__init__(service_name="bot_constructor")
        self.base_url = settings.bot_constructor_url.rstrip('/')
        self._session = session or aiohttp.ClientSession()
        self.timeout = aiohttp.ClientTimeout(total=settings.integration_timeout)

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Bot Constructor service.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data
            
        Raises:
            IntegrationError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self._session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            ) as response:
                if response.status == 404:
                    raise BotNotFoundError(f"Bot not found: {response.status}")
                elif response.status == 422:
                    raise BotValidationError(f"Invalid bot data: {response.status}")
                elif response.status == 400:
                    raise BotCreationError(f"Bot creation failed: {response.status}")
                elif response.status >= 400:
                    raise IntegrationError(
                        f"Bot Constructor request failed: {response.status}"
                    )
                    
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise IntegrationError(f"Bot Constructor request failed: {str(e)}")

    async def get_bot(self, bot_id: str) -> Bot:
        """Get bot by ID.
        
        Args:
            bot_id: Bot identifier
            
        Returns:
            Bot instance
            
        Raises:
            BotNotFoundError: If bot not found
            IntegrationError: If request fails
        """
        data = await self._make_request("GET", f"/bots/{bot_id}")
        return Bot(**data)

    async def list_bots(
        self,
        page: int = 1,
        page_size: int = 50
    ) -> BotList:
        """Get list of bots with pagination.
        
        Args:
            page: Page number
            page_size: Items per page
            
        Returns:
            List of bots with pagination info
            
        Raises:
            IntegrationError: If request fails
        """
        params = {"page": page, "page_size": page_size}
        data = await self._make_request("GET", "/bots", params=params)
        return BotList(**data)

    async def create_bot(self, bot_data: BotCreate) -> Bot:
        """Create new bot.
        
        Args:
            bot_data: Bot creation data
            
        Returns:
            Created bot instance
            
        Raises:
            BotValidationError: If bot data is invalid
            BotCreationError: If bot creation fails
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "POST",
            "/bots",
            json=bot_data.model_dump()
        )
        return Bot(**data)

    async def update_bot(self, bot_id: str, bot_data: BotUpdate) -> Bot:
        """Update existing bot.
        
        Args:
            bot_id: Bot identifier
            bot_data: Bot update data
            
        Returns:
            Updated bot instance
            
        Raises:
            BotNotFoundError: If bot not found
            BotValidationError: If bot data is invalid
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "PUT",
            f"/bots/{bot_id}",
            json=bot_data.model_dump(exclude_unset=True)
        )
        return Bot(**data)

    async def delete_bot(self, bot_id: str) -> None:
        """Delete bot by ID.
        
        Args:
            bot_id: Bot identifier
            
        Raises:
            BotNotFoundError: If bot not found
            IntegrationError: If request fails
        """
        await self._make_request("DELETE", f"/bots/{bot_id}")

    async def get_bot_response(
        self,
        bot_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> BotResponse:
        """Get bot response for user input.
        
        Args:
            bot_id: Bot identifier
            user_input: User message text
            context: Optional conversation context
            
        Returns:
            Bot response
            
        Raises:
            BotNotFoundError: If bot not found
            IntegrationError: If request fails
        """
        data = {
            "user_input": user_input,
            "context": context or {}
        }
        response_data = await self._make_request(
            "POST",
            f"/bots/{bot_id}/response",
            json=data
        )
        return BotResponse(**response_data)

    async def healthcheck(self) -> bool:
        """Check Bot Constructor service health.
        
        Returns:
            True if service is healthy
            
        Raises:
            IntegrationError: If health check fails
        """
        try:
            await self._make_request("GET", "/health")
            return True
        except IntegrationError:
            return False