# services\api_gateway\src\integrations\data_storage\client.py
from typing import Optional, List, Dict, Any, Union
import aiohttp
from aiohttp import ClientSession
from src.core.abstractions.integrations import BaseIntegrationClient
from src.core.config import Settings
from src.core.exceptions import (
    IntegrationError,
    DataNotFoundError,
    DataValidationError,
    StorageError
)
from src.integrations.data_storage.schemas import (
    DataItem,
    DataItemCreate,
    DataItemUpdate,
    DataItemList,
    DataQuery,
    StorageStats
)


class DataStorageClient(BaseIntegrationClient):
    """Client for interacting with Data Storage service."""
    
    def __init__(self, settings: Settings, session: Optional[ClientSession] = None):
        """Initialize Data Storage client.
        
        Args:
            settings: Application settings
            session: Optional aiohttp ClientSession
        """
        super().__init__(service_name="data_storage")
        self.base_url = settings.data_storage_url.rstrip('/')
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
        """Make HTTP request to Data Storage service.
        
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
                    raise DataNotFoundError(f"Data not found: {response.status}")
                elif response.status == 422:
                    raise DataValidationError(f"Invalid data format: {response.status}")
                elif response.status >= 400:
                    raise StorageError(f"Storage operation failed: {response.status}")
                    
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise IntegrationError(f"Data Storage request failed: {str(e)}")

    async def get_item(self, item_id: str) -> DataItem:
        """Get data item by ID.
        
        Args:
            item_id: Item identifier
            
        Returns:
            Data item
            
        Raises:
            DataNotFoundError: If item not found
            IntegrationError: If request fails
        """
        data = await self._make_request("GET", f"/items/{item_id}")
        return DataItem(**data)

    async def list_items(
        self,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> DataItemList:
        """Get list of data items with pagination and filtering.
        
        Args:
            page: Page number
            page_size: Items per page
            filters: Optional filter parameters
            
        Returns:
            List of data items with pagination info
            
        Raises:
            IntegrationError: If request fails
        """
        params = {
            "page": page,
            "page_size": page_size,
            **(filters or {})
        }
        data = await self._make_request("GET", "/items", params=params)
        return DataItemList(**data)

    async def create_item(
        self,
        item_data: DataItemCreate,
        workspace_id: Optional[str] = None
    ) -> DataItem:
        """Create new data item.
        
        Args:
            item_data: Item creation data
            workspace_id: Optional workspace identifier
            
        Returns:
            Created data item
            
        Raises:
            DataValidationError: If item data is invalid
            StorageError: If creation fails
            IntegrationError: If request fails
        """
        params = {"workspace_id": workspace_id} if workspace_id else {}
        data = await self._make_request(
            "POST",
            "/items",
            json=item_data.model_dump(),
            params=params
        )
        return DataItem(**data)

    async def update_item(
        self,
        item_id: str,
        item_data: DataItemUpdate
    ) -> DataItem:
        """Update existing data item.
        
        Args:
            item_id: Item identifier
            item_data: Item update data
            
        Returns:
            Updated data item
            
        Raises:
            DataNotFoundError: If item not found
            DataValidationError: If item data is invalid
            StorageError: If update fails
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "PUT",
            f"/items/{item_id}",
            json=item_data.model_dump(exclude_unset=True)
        )
        return DataItem(**data)

    async def delete_item(self, item_id: str) -> None:
        """Delete data item by ID.
        
        Args:
            item_id: Item identifier
            
        Raises:
            DataNotFoundError: If item not found
            StorageError: If deletion fails
            IntegrationError: If request fails
        """
        await self._make_request("DELETE", f"/items/{item_id}")

    async def search_items(self, query: DataQuery) -> List[DataItem]:
        """Search data items by query.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of matching data items
            
        Raises:
            DataValidationError: If query is invalid
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "POST",
            "/items/search",
            json=query.model_dump()
        )
        return [DataItem(**item) for item in data]

    async def get_storage_stats(
        self,
        workspace_id: Optional[str] = None
    ) -> StorageStats:
        """Get storage statistics.
        
        Args:
            workspace_id: Optional workspace identifier
            
        Returns:
            Storage statistics
            
        Raises:
            IntegrationError: If request fails
        """
        params = {"workspace_id": workspace_id} if workspace_id else {}
        data = await self._make_request("GET", "/stats", params=params)
        return StorageStats(**data)

    async def bulk_delete(
        self,
        item_ids: List[str],
        workspace_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """Delete multiple data items.
        
        Args:
            item_ids: List of item identifiers
            workspace_id: Optional workspace identifier
            
        Returns:
            Dictionary mapping item IDs to deletion success status
            
        Raises:
            StorageError: If bulk deletion fails
            IntegrationError: If request fails
        """
        params = {"workspace_id": workspace_id} if workspace_id else {}
        data = await self._make_request(
            "POST",
            "/items/bulk-delete",
            json={"item_ids": item_ids},
            params=params
        )
        return data

    async def healthcheck(self) -> bool:
        """Check Data Storage service health.
        
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