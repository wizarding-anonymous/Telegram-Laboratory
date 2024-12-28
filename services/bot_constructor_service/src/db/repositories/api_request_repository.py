from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.api_request_model import ApiRequest
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class ApiRequestRepository:
    """
    Repository for performing database operations on api request entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the ApiRequestRepository with a database session."""
        self.session = session
        logging_client.info("ApiRequestRepository initialized")

    @handle_exceptions
    async def create(self, api_request_data: dict) -> ApiRequest:
        """Creates a new api request block in the database."""
        logging_client.info(f"Creating new api request block with data: {api_request_data}")
        api_request = ApiRequest(**api_request_data)
        self.session.add(api_request)
        await self.session.commit()
        await self.session.refresh(api_request)
        logging_client.info(f"Api request block with id: {api_request.id} created successfully")
        return api_request

    @handle_exceptions
    async def get_by_id(self, api_request_id: int) -> Optional[ApiRequest]:
        """Retrieves a api request block by its ID."""
        logging_client.info(f"Getting api request block by id: {api_request_id}")
        api_request = await self.session.get(ApiRequest, api_request_id)
        if api_request:
            logging_client.info(f"Api request block with id: {api_request_id} retrieved successfully")
        else:
            logging_client.warning(f"Api request block with id: {api_request_id} not found")
        return api_request

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[ApiRequest]:
        """Retrieves all api request blocks for a specific bot."""
        logging_client.info(f"Getting all api request blocks for bot_id: {bot_id}")
        query = select(ApiRequest).where(ApiRequest.bot_id == bot_id)
        result = await self.session.execute(query)
        api_requests = result.scalars().all()
        logging_client.info(f"Found {len(api_requests)} api request blocks for bot_id: {bot_id}")
        return list(api_requests)

    @handle_exceptions
    async def update(self, api_request_id: int, api_request_data: dict) -> Optional[ApiRequest]:
        """Updates an existing api request block."""
        logging_client.info(f"Updating api request block with id: {api_request_id} with data: {api_request_data}")
        api_request = await self.session.get(ApiRequest, api_request_id)
        if api_request:
            for key, value in api_request_data.items():
                setattr(api_request, key, value)
            await self.session.commit()
            await self.session.refresh(api_request)
            logging_client.info(f"Api request block with id: {api_request_id} updated successfully")
            return api_request
        logging_client.warning(f"Api request block with id: {api_request_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, api_request_id: int) -> bool:
        """Deletes a api request block by its ID."""
        logging_client.info(f"Deleting api request block with id: {api_request_id}")
        api_request = await self.session.get(ApiRequest, api_request_id)
        if api_request:
            await self.session.delete(api_request)
            await self.session.commit()
            logging_client.info(f"Api request block with id: {api_request_id} deleted successfully")
            return True
        logging_client.warning(f"Api request block with id: {api_request_id} not found for delete")
        return False