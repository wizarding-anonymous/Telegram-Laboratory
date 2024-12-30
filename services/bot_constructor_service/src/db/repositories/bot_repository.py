from typing import List, Dict, Any, Tuple, Optional
from fastapi import HTTPException
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.models import Bot
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name="bot_constructor")


class BotRepository:
    """
    Repository for managing bot data in the database.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        logging_client.info("BotRepository initialized")

    @handle_exceptions
    async def create(self, bot_data: Dict[str, Any], user_id: int) -> Bot:
        """Creates a new bot."""
        logging_client.info(f"Creating bot with data: {bot_data} for user {user_id}")
        bot = Bot(**bot_data, user_id=user_id)
        self.session.add(bot)
        await self.session.commit()
        await self.session.refresh(bot)
        logging_client.info(f"Bot with id: {bot.id} created successfully")
        return bot

    @handle_exceptions
    async def get_by_id(self, bot_id: int) -> Optional[Bot]:
        """Gets a bot by its ID."""
        logging_client.info(f"Getting bot with id: {bot_id}")
        result = await self.session.execute(select(Bot).where(Bot.id == bot_id))
        bot = result.scalar_one_or_none()
        if bot:
            logging_client.info(f"Bot with id: {bot_id} retrieved successfully")
        else:
             logging_client.warning(f"Bot with id: {bot_id} not found")
        return bot

    @handle_exceptions
    async def list_paginated(self, page: int, page_size: int, user_id: int) -> Tuple[List[Bot], int]:
        """Gets a paginated list of bots for a specific user."""
        logging_client.info(f"Getting paginated list of bots for user_id: {user_id}")
        offset = (page - 1) * page_size
        
        count_query = await self.session.execute(select(func.count()).where(Bot.user_id == user_id))
        total = count_query.scalar_one()
        
        query = (
            select(Bot)
            .where(Bot.user_id == user_id)
            .order_by(Bot.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.session.execute(query)
        bots = list(result.scalars().all())
        logging_client.info(f"Found {len(bots)} of {total} bots for user_id: {user_id}")
        return bots, total

    @handle_exceptions
    async def list_by_user_id(self, user_id: int) -> List[Bot]:
        """Gets a list of bots for a specific user ID."""
        logging_client.info(f"Getting list of bots for user_id: {user_id}")
        result = await self.session.execute(select(Bot).where(Bot.user_id == user_id))
        bots = list(result.scalars().all())
        logging_client.info(f"Found {len(bots)} bots for user_id: {user_id}")
        return bots

    @handle_exceptions
    async def update(self, bot_id: int, bot_data: Dict[str, Any]) -> Bot:
        """Updates an existing bot."""
        logging_client.info(f"Updating bot with id: {bot_id}")
        query = update(Bot).where(Bot.id == bot_id).values(bot_data).returning(Bot)
        result = await self.session.execute(query)
        updated_bot = result.scalar_one_or_none()
        if not updated_bot:
             logging_client.warning(f"Bot with id: {bot_id} not found")
             raise HTTPException(status_code=404, detail="Bot not found")
        await self.session.commit()
        logging_client.info(f"Bot with id: {bot_id} updated successfully")
        return updated_bot

    @handle_exceptions
    async def delete(self, bot_id: int) -> None:
        """Deletes a bot."""
        logging_client.info(f"Deleting bot with id: {bot_id}")
        query = delete(Bot).where(Bot.id == bot_id)
        await self.session.execute(query)
        await self.session.commit()
        logging_client.info(f"Bot with id: {bot_id} deleted successfully")