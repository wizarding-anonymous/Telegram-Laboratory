# services\user_dashboard\src\core\bot_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from app.models import Bot
from app.schemas.bot_schema import BotCreateRequest, BotUpdateRequest, BotResponse
from datetime import datetime
import logging

logger = logging.getLogger("bot_service")


class BotService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_bot(self, user_id: int, bot_data: BotCreateRequest) -> BotResponse:
        """
        Создает нового бота для пользователя.
        """
        try:
            new_bot = Bot(
                name=bot_data.name,
                description=bot_data.description,
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            self.db.add(new_bot)
            await self.db.commit()
            await self.db.refresh(new_bot)

            logger.info(f"Bot created: {new_bot.name} (ID: {new_bot.id}) for user {user_id}")
            return BotResponse.from_orm(new_bot)
        except Exception as e:
            logger.error(f"Error creating bot for user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bot")

    async def get_all_user_bots(self, user_id: int) -> list[BotResponse]:
        """
        Возвращает список всех ботов пользователя.
        """
        try:
            result = await self.db.execute(
                select(Bot).where(Bot.user_id == user_id).options(joinedload(Bot.user))
            )
            bots = result.scalars().all()
            return [BotResponse.from_orm(bot) for bot in bots]
        except Exception as e:
            logger.error(f"Error fetching bots for user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch bots")

    async def get_bot_by_id(self, bot_id: int, user_id: int) -> BotResponse:
        """
        Возвращает данные бота по ID.
        """
        try:
            result = await self.db.execute(
                select(Bot).where(Bot.id == bot_id, Bot.user_id == user_id)
            )
            bot = result.scalar_one_or_none()
            if not bot:
                logger.warning(f"Bot not found: ID {bot_id} for user {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
            return BotResponse.from_orm(bot)
        except Exception as e:
            logger.error(f"Error fetching bot ID {bot_id} for user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch bot")

    async def update_bot(self, bot_id: int, user_id: int, bot_data: BotUpdateRequest) -> BotResponse:
        """
        Обновляет данные существующего бота.
        """
        try:
            result = await self.db.execute(
                select(Bot).where(Bot.id == bot_id, Bot.user_id == user_id)
            )
            bot = result.scalar_one_or_none()
            if not bot:
                logger.warning(f"Bot not found: ID {bot_id} for user {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

            if bot_data.name:
                bot.name = bot_data.name
            if bot_data.description:
                bot.description = bot_data.description
            bot.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(bot)

            logger.info(f"Bot updated: ID {bot_id} for user {user_id}")
            return BotResponse.from_orm(bot)
        except Exception as e:
            logger.error(f"Error updating bot ID {bot_id} for user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update bot")

    async def delete_bot(self, bot_id: int, user_id: int) -> None:
        """
        Удаляет бота по ID.
        """
        try:
            result = await self.db.execute(
                select(Bot).where(Bot.id == bot_id, Bot.user_id == user_id)
            )
            bot = result.scalar_one_or_none()
            if not bot:
                logger.warning(f"Bot not found: ID {bot_id} for user {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

            await self.db.delete(bot)
            await self.db.commit()

            logger.info(f"Bot deleted: ID {bot_id} for user {user_id}")
        except Exception as e:
            logger.error(f"Error deleting bot ID {bot_id} for user {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete bot")
