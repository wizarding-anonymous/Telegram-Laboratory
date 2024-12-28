from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.message_model import Message
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class MessageRepository:
    """
    Repository for performing database operations on message entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the MessageRepository with a database session."""
        self.session = session
        logging_client.info("MessageRepository initialized")

    @handle_exceptions
    async def create(self, message_data: dict) -> Message:
        """Creates a new message in the database."""
        logging_client.info(f"Creating new message with data: {message_data}")
        message = Message(**message_data)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        logging_client.info(f"Message with id: {message.id} created successfully")
        return message

    @handle_exceptions
    async def get_by_id(self, message_id: int) -> Optional[Message]:
        """Retrieves a message by its ID."""
        logging_client.info(f"Getting message by id: {message_id}")
        message = await self.session.get(Message, message_id)
        if message:
            logging_client.info(f"Message with id: {message_id} retrieved successfully")
        else:
             logging_client.warning(f"Message with id: {message_id} not found")
        return message

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Message]:
        """Retrieves all messages for a specific bot."""
        logging_client.info(f"Getting all messages for bot_id: {bot_id}")
        query = select(Message).where(Message.bot_id == bot_id)
        result = await self.session.execute(query)
        messages = result.scalars().all()
        logging_client.info(f"Found {len(messages)} messages for bot_id: {bot_id}")
        return list(messages)

    @handle_exceptions
    async def update(self, message_id: int, message_data: dict) -> Optional[Message]:
        """Updates an existing message."""
        logging_client.info(f"Updating message with id: {message_id} with data: {message_data}")
        message = await self.session.get(Message, message_id)
        if message:
            for key, value in message_data.items():
                setattr(message, key, value)
            await self.session.commit()
            await self.session.refresh(message)
            logging_client.info(f"Message with id: {message_id} updated successfully")
            return message
        logging_client.warning(f"Message with id: {message_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, message_id: int) -> bool:
        """Deletes a message by its ID."""
        logging_client.info(f"Deleting message with id: {message_id}")
        message = await self.session.get(Message, message_id)
        if message:
            await self.session.delete(message)
            await self.session.commit()
            logging_client.info(f"Message with id: {message_id} deleted successfully")
            return True
        logging_client.warning(f"Message with id: {message_id} not found for delete")
        return False