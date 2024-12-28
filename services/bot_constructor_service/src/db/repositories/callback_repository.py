from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.callback_model import Callback
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class CallbackRepository:
    """
    Repository for performing database operations on callback entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the CallbackRepository with a database session."""
        self.session = session
        logging_client.info("CallbackRepository initialized")

    @handle_exceptions
    async def create(self, callback_data: dict) -> Callback:
        """Creates a new callback in the database."""
        logging_client.info(f"Creating new callback with data: {callback_data}")
        callback = Callback(**callback_data)
        self.session.add(callback)
        await self.session.commit()
        await self.session.refresh(callback)
        logging_client.info(f"Callback with id: {callback.id} created successfully")
        return callback

    @handle_exceptions
    async def get_by_id(self, callback_id: int) -> Optional[Callback]:
        """Retrieves a callback by its ID."""
        logging_client.info(f"Getting callback by id: {callback_id}")
        callback = await self.session.get(Callback, callback_id)
        if callback:
           logging_client.info(f"Callback with id: {callback_id} retrieved successfully")
        else:
            logging_client.warning(f"Callback with id: {callback_id} not found")
        return callback

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Callback]:
        """Retrieves all callbacks for a specific bot."""
        logging_client.info(f"Getting all callbacks for bot_id: {bot_id}")
        query = select(Callback).where(Callback.bot_id == bot_id)
        result = await self.session.execute(query)
        callbacks = result.scalars().all()
        logging_client.info(f"Found {len(callbacks)} callbacks for bot_id: {bot_id}")
        return list(callbacks)

    @handle_exceptions
    async def update(self, callback_id: int, callback_data: dict) -> Optional[Callback]:
        """Updates an existing callback."""
        logging_client.info(f"Updating callback with id: {callback_id} with data: {callback_data}")
        callback = await self.session.get(Callback, callback_id)
        if callback:
            for key, value in callback_data.items():
                setattr(callback, key, value)
            await self.session.commit()
            await self.session.refresh(callback)
            logging_client.info(f"Callback with id: {callback_id} updated successfully")
            return callback
        logging_client.warning(f"Callback with id: {callback_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, callback_id: int) -> bool:
        """Deletes a callback by its ID."""
        logging_client.info(f"Deleting callback with id: {callback_id}")
        callback = await self.session.get(Callback, callback_id)
        if callback:
            await self.session.delete(callback)
            await self.session.commit()
            logging_client.info(f"Callback with id: {callback_id} deleted successfully")
            return True
        logging_client.warning(f"Callback with id: {callback_id} not found for delete")
        return False