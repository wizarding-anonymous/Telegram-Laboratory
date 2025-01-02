from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Bot
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class BotRepository:
    """
    Repository for performing CRUD operations on the Bot model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, **bot_data) -> Bot:
        """
        Creates a new bot in the database.
        """
        logger.info(f"Creating bot with data: {bot_data}")
        try:
            bot = Bot(**bot_data)
            self.session.add(bot)
            await self.session.commit()
            await self.session.refresh(bot)
            logger.info(f"Bot created successfully. Bot id: {bot.id}")
            return bot
        except Exception as e:
            logger.error(f"Error creating bot: {e}")
            raise DatabaseException(f"Failed to create bot: {e}") from e

    @handle_exceptions
    async def get(self, bot_id: int, user_id: int) -> Optional[Bot]:
        """
        Retrieves a bot by its ID and user_id.
        """
        logger.info(f"Getting bot with ID: {bot_id}, user_id: {user_id}")
        try:
            query = select(Bot).where(Bot.id == bot_id, Bot.user_id == user_id)
            result = await self.session.execute(query)
            bot = result.scalar_one_or_none()
            if bot:
                logger.debug(f"Bot with ID {bot_id} found.")
            else:
                logger.warning(f"Bot with ID {bot_id} not found.")
            return bot
        except Exception as e:
            logger.error(f"Error getting bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to get bot {bot_id}: {e}") from e

    @handle_exceptions
    async def get_all(self, user_id: int) -> List[Bot]:
        """
        Retrieves all bots of the current user.
        """
        logger.info(f"Getting all bots for user ID: {user_id}")
        try:
           query = select(Bot).where(Bot.user_id == user_id)
           result = await self.session.execute(query)
           bots = list(result.scalars().all())
           logger.debug(f"Found {len(bots)} bots for user {user_id}")
           return bots
        except Exception as e:
            logger.error(f"Error getting all bots for user {user_id}: {e}")
            raise DatabaseException(f"Failed to get all bots for user {user_id}: {e}") from e

    @handle_exceptions
    async def update(self, bot_id: int, **bot_data) -> Optional[Bot]:
        """
        Updates an existing bot by its ID.
        """
        logger.info(f"Updating bot with ID: {bot_id}, data: {bot_data}")
        try:
            query = select(Bot).where(Bot.id == bot_id)
            result = await self.session.execute(query)
            bot = result.scalar_one_or_none()
            if bot:
                for key, value in bot_data.items():
                    setattr(bot, key, value)
                await self.session.commit()
                await self.session.refresh(bot)
                logger.info(f"Bot with ID {bot_id} updated successfully.")
            else:
                logger.warning(f"Bot with ID {bot_id} not found for update.")
            return bot
        except Exception as e:
            logger.error(f"Error updating bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to update bot {bot_id}: {e}") from e

    @handle_exceptions
    async def delete(self, bot_id: int) -> None:
        """
        Deletes a bot by its ID.
        """
        logger.info(f"Deleting bot with ID: {bot_id}")
        try:
            query = delete(Bot).where(Bot.id == bot_id)
            await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Bot with ID {bot_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to delete bot {bot_id}: {e}") from e