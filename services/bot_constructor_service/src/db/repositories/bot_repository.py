# services\bot_constructor_service\src\db\repositories\bot_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from src.db.models.bot_model import Bot
from typing import Optional


class BotRepository:
    """
    Repository for managing Bot database operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session.
        """
        self.session = session

    async def get_by_id(self, bot_id: int) -> Optional[Bot]:
        """
        Retrieve a bot by its ID.

        Args:
            bot_id (int): ID of the bot.

        Returns:
            Bot | None: The bot if found, otherwise None.
        """
        query = select(Bot).where(Bot.id == bot_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Bot]:
        """
        Retrieve all bots for a specific user with pagination.

        Args:
            user_id (int): ID of the user.
            skip (int): Number of records to skip.
            limit (int): Maximum number of records to retrieve.

        Returns:
            list[Bot]: List of bots.
        """
        query = select(Bot).where(Bot.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, bot_data: dict) -> Bot:
        """
        Create a new bot.

        Args:
            bot_data (dict): Data for the new bot.

        Returns:
            Bot: The created bot.
        """
        bot = Bot(**bot_data)
        self.session.add(bot)
        await self.session.flush()  # Flush to ensure the bot gets an ID before commit.
        await self.session.commit()
        return bot

    async def update(self, bot_id: int, bot_data: dict) -> Optional[Bot]:
        """
        Update an existing bot.

        Args:
            bot_id (int): ID of the bot to update.
            bot_data (dict): Data to update.

        Returns:
            Bot | None: The updated bot if found, otherwise None.
        """
        query = update(Bot).where(Bot.id == bot_id).values(**bot_data).returning(Bot)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, bot_id: int) -> bool:
        """
        Delete a bot by its ID.

        Args:
            bot_id (int): ID of the bot to delete.

        Returns:
            bool: True if the bot was deleted, False otherwise.
        """
        query = delete(Bot).where(Bot.id == bot_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
