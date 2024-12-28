from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.keyboard_model import Keyboard
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class KeyboardRepository:
    """
    Repository for performing database operations on keyboard entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the KeyboardRepository with a database session."""
        self.session = session
        logging_client.info("KeyboardRepository initialized")

    @handle_exceptions
    async def create(self, keyboard_data: dict) -> Keyboard:
        """Creates a new keyboard in the database."""
        logging_client.info(f"Creating new keyboard with data: {keyboard_data}")
        keyboard = Keyboard(**keyboard_data)
        self.session.add(keyboard)
        await self.session.commit()
        await self.session.refresh(keyboard)
        logging_client.info(f"Keyboard with id: {keyboard.id} created successfully")
        return keyboard

    @handle_exceptions
    async def get_by_id(self, keyboard_id: int) -> Optional[Keyboard]:
        """Retrieves a keyboard by its ID."""
        logging_client.info(f"Getting keyboard by id: {keyboard_id}")
        keyboard = await self.session.get(Keyboard, keyboard_id)
        if keyboard:
           logging_client.info(f"Keyboard with id: {keyboard_id} retrieved successfully")
        else:
             logging_client.warning(f"Keyboard with id: {keyboard_id} not found")
        return keyboard

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Keyboard]:
        """Retrieves all keyboards for a specific bot."""
        logging_client.info(f"Getting all keyboards for bot_id: {bot_id}")
        query = select(Keyboard).where(Keyboard.bot_id == bot_id)
        result = await self.session.execute(query)
        keyboards = result.scalars().all()
        logging_client.info(f"Found {len(keyboards)} keyboards for bot_id: {bot_id}")
        return list(keyboards)

    @handle_exceptions
    async def update(self, keyboard_id: int, keyboard_data: dict) -> Optional[Keyboard]:
        """Updates an existing keyboard."""
        logging_client.info(f"Updating keyboard with id: {keyboard_id} with data: {keyboard_data}")
        keyboard = await self.session.get(Keyboard, keyboard_id)
        if keyboard:
            for key, value in keyboard_data.items():
                setattr(keyboard, key, value)
            await self.session.commit()
            await self.session.refresh(keyboard)
            logging_client.info(f"Keyboard with id: {keyboard_id} updated successfully")
            return keyboard
        logging_client.warning(f"Keyboard with id: {keyboard_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, keyboard_id: int) -> bool:
        """Deletes a keyboard by its ID."""
        logging_client.info(f"Deleting keyboard with id: {keyboard_id}")
        keyboard = await self.session.get(Keyboard, keyboard_id)
        if keyboard:
            await self.session.delete(keyboard)
            await self.session.commit()
            logging_client.info(f"Keyboard with id: {keyboard_id} deleted successfully")
            return True
        logging_client.warning(f"Keyboard with id: {keyboard_id} not found for delete")
        return False