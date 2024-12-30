from typing import List, Dict, Any, Tuple, Optional
from fastapi import HTTPException
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.models import CustomFilter
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name="bot_constructor")


class CustomFilterRepository:
    """
    Repository for managing custom filter data in the database.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        logging_client.info("CustomFilterRepository initialized")

    @handle_exceptions
    async def create(self, bot_id: int, custom_filter_data: Dict[str, Any]) -> CustomFilter:
        """Creates a new custom filter block."""
        logging_client.info(f"Creating custom filter block for bot_id: {bot_id}")
        custom_filter = CustomFilter(**custom_filter_data, bot_id=bot_id)
        self.session.add(custom_filter)
        await self.session.commit()
        await self.session.refresh(custom_filter)
        logging_client.info(f"Custom filter block with id: {custom_filter.id} created successfully")
        return custom_filter

    @handle_exceptions
    async def get_by_id(self, custom_filter_id: int) -> Optional[CustomFilter]:
        """Gets a custom filter block by its ID."""
        logging_client.info(f"Getting custom filter block with id: {custom_filter_id}")
        result = await self.session.execute(select(CustomFilter).where(CustomFilter.id == custom_filter_id))
        custom_filter = result.scalar_one_or_none()
        if custom_filter:
            logging_client.info(f"Custom filter block with id: {custom_filter_id} retrieved successfully")
        else:
            logging_client.warning(f"Custom filter block with id: {custom_filter_id} not found")
        return custom_filter

    @handle_exceptions
    async def list_by_bot_id(self, bot_id: int) -> List[CustomFilter]:
         """Gets a list of custom filter blocks for a specific bot."""
         logging_client.info(f"Getting list of custom filter blocks for bot_id: {bot_id}")
         query = select(CustomFilter).where(CustomFilter.bot_id == bot_id)
         result = await self.session.execute(query)
         custom_filters = list(result.scalars().all())
         logging_client.info(f"Found {len(custom_filters)} custom filter blocks for bot_id: {bot_id}")
         return custom_filters


    @handle_exceptions
    async def update(self, custom_filter_id: int, custom_filter_data: Dict[str, Any]) -> CustomFilter:
        """Updates an existing custom filter block."""
        logging_client.info(f"Updating custom filter block with id: {custom_filter_id}")
        query = (
            update(CustomFilter)
            .where(CustomFilter.id == custom_filter_id)
            .values(custom_filter_data)
            .returning(CustomFilter)
        )
        result = await self.session.execute(query)
        updated_custom_filter = result.scalar_one_or_none()
        if not updated_custom_filter:
             logging_client.warning(f"Custom filter block with id: {custom_filter_id} not found")
             raise HTTPException(status_code=404, detail="Custom filter block not found")
        await self.session.commit()
        logging_client.info(f"Custom filter block with id: {custom_filter_id} updated successfully")
        return updated_custom_filter

    @handle_exceptions
    async def delete(self, custom_filter_id: int) -> None:
        """Deletes a custom filter block."""
        logging_client.info(f"Deleting custom filter block with id: {custom_filter_id}")
        query = delete(CustomFilter).where(CustomFilter.id == custom_filter_id)
        await self.session.execute(query)
        await self.session.commit()
        logging_client.info(f"Custom filter block with id: {custom_filter_id} deleted successfully")