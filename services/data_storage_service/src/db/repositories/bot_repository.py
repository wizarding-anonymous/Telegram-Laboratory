# services/data_storage_service/src/db/repositories/bot_repository.py

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.utils.helpers import MigrationException
from src.db.models.bot_model import Bot
from src.config import settings
from loguru import logger


class BotRepository:
    """
    Репозиторий для работы с таблицей 'bots' в базе данных.
    Отвечает за CRUD-операции с данными о боте.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с сессией базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.session = session

    async def get_by_id(self, bot_id: int) -> Optional[Bot]:
        """
        Получить бота по его ID.

        Args:
            bot_id (int): ID бота.

        Returns:
            Bot | None: Возвращает объект Bot, если найден, иначе None.
        """
        logger.debug(f"Fetching bot with ID: {bot_id}")
        query = select(Bot).where(Bot.id == bot_id)
        result = await self.session.execute(query)
        bot = result.scalar_one_or_none()
        if bot:
            logger.debug(f"Bot found: {bot}")
        else:
            logger.debug(f"No bot found with ID: {bot_id}")
        return bot

    async def get_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Bot]:
        """
        Получить список ботов для конкретного пользователя с пагинацией.

        Args:
            user_id (int): ID пользователя.
            skip (int): Количество записей для пропуска.
            limit (int): Максимальное количество записей для извлечения.

        Returns:
            List[Bot]: Список объектов Bot.
        """
        logger.debug(f"Fetching bots for user ID: {user_id} with skip={skip} and limit={limit}")
        query = select(Bot).where(Bot.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        bots = result.scalars().all()
        logger.debug(f"Number of bots fetched: {len(bots)}")
        return bots

    async def create(self, bot_data: dict, user_id: int) -> Bot:
        """
        Создать нового бота.

        Args:
            bot_data (dict): Данные для создания нового бота.
            user_id (int): ID пользователя, который создает бота.

        Returns:
            Bot: Созданный объект Bot.
        """
        logger.debug(f"Creating a new bot for user ID: {user_id} with data: {bot_data}")
        # Проверка миграций перед созданием бота
        try:
            await Bot.check_migrations_status(self.session)
            logger.debug("Migrations are up-to-date.")
        except MigrationException as e:
            logger.error(f"Migration check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        bot = Bot(**bot_data, user_id=user_id)
        self.session.add(bot)
        try:
            await self.session.commit()
            await self.session.refresh(bot)
            logger.info(f"Bot created successfully: {bot}")
            return bot
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating bot: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create bot.")

    async def update(self, bot_id: int, bot_data: dict) -> Optional[Bot]:
        """
        Обновить данные бота по его ID.

        Args:
            bot_id (int): ID бота для обновления.
            bot_data (dict): Данные для обновления.

        Returns:
            Bot | None: Обновленный объект Bot, если найден, иначе None.
        """
        logger.debug(f"Updating bot ID: {bot_id} with data: {bot_data}")
        # Проверка миграций перед обновлением данных о боте
        try:
            await Bot.check_migrations_status(self.session)
            logger.debug("Migrations are up-to-date.")
        except MigrationException as e:
            logger.error(f"Migration check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        query = update(Bot).where(Bot.id == bot_id).values(**bot_data).returning(Bot)
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            updated_bot = result.scalar_one_or_none()
            if updated_bot:
                logger.info(f"Bot updated successfully: {updated_bot}")
            else:
                logger.warning(f"No bot found with ID: {bot_id} to update.")
            return updated_bot
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating bot: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update bot.")

    async def delete(self, bot_id: int) -> bool:
        """
        Удалить бота по его ID.

        Args:
            bot_id (int): ID бота для удаления.

        Returns:
            bool: True, если бот был удален, иначе False.
        """
        logger.debug(f"Deleting bot with ID: {bot_id}")
        # Проверка миграций перед удалением бота
        try:
            await Bot.check_migrations_status(self.session)
            logger.debug("Migrations are up-to-date.")
        except MigrationException as e:
            logger.error(f"Migration check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        query = delete(Bot).where(Bot.id == bot_id)
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            if result.rowcount > 0:
                logger.info(f"Bot with ID {bot_id} deleted successfully.")
                return True
            else:
                logger.warning(f"No bot found with ID: {bot_id} to delete.")
                return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting bot: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete bot.")
