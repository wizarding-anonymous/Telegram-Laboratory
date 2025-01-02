from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

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
        bot = Bot(**bot_data)
        self.session.add(bot)
        await self.session.commit()
        await self.session.refresh(bot)
        return bot

    @handle_exceptions
    async def get(self, bot_id: int, user_id: int) -> Optional[Bot]:
        """
        Retrieves a bot by its ID and user_id.
        """
        query = select(Bot).where(Bot.id == bot_id, Bot.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    @handle_exceptions
    async def get_all(self, user_id: int) -> List[Bot]:
        """
        Retrieves all bots of the current user.
        """
        query = select(Bot).where(Bot.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    @handle_exceptions
    async def update(self, bot_id: int, **bot_data) -> Optional[Bot]:
        """
        Updates an existing bot by its ID.
        """
        query = select(Bot).where(Bot.id == bot_id)
        result = await self.session.execute(query)
        bot = result.scalar_one_or_none()
        if bot:
            for key, value in bot_data.items():
                setattr(bot, key, value)
            await self.session.commit()
            await self.session.refresh(bot)
        return bot

    @handle_exceptions
    async def delete(self, bot_id: int) -> None:
        """
        Deletes a bot by its ID.
        """
        query = delete(Bot).where(Bot.id == bot_id)
        await self.session.execute(query)
        await self.session.commit()