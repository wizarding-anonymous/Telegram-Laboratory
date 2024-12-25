# services/data_storage_service/src/db/repositories/metadata_repository.py

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.utils.helpers import MigrationException
from src.db.models.metadata_model import Metadata
from src.config import settings
from loguru import logger


class MetadataRepository:
    """
    Репозиторий для работы с таблицей 'metadata' в базе данных.
    Отвечает за CRUD-операции с метаданными ботов.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с сессией базы данных.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.session = session

    async def get_by_id(self, metadata_id: int) -> Optional[Metadata]:
        """
        Получить метаданные по их ID.

        Args:
            metadata_id (int): ID метаданных.

        Returns:
            Metadata | None: Возвращает объект Metadata, если найден, иначе None.
        """
        logger.debug(f"Fetching metadata with ID: {metadata_id}")
        query = select(Metadata).where(Metadata.id == metadata_id)
        result = await self.session.execute(query)
        metadata = result.scalar_one_or_none()
        if metadata:
            logger.debug(f"Metadata found: {metadata}")
        else:
            logger.debug(f"No metadata found with ID: {metadata_id}")
        return metadata

    async def get_by_bot_id(
        self, bot_id: int, skip: int = 0, limit: int = 100
    ) -> List[Metadata]:
        """
        Получить все метаданные для конкретного бота с пагинацией.

        Args:
            bot_id (int): ID бота.
            skip (int): Количество записей для пропуска (для пагинации).
            limit (int): Максимальное количество записей для извлечения.

        Returns:
            List[Metadata]: Список объектов Metadata.
        """
        logger.debug(
            f"Fetching metadata for bot ID: {bot_id} with skip={skip} and limit={limit}"
        )
        query = (
            select(Metadata)
            .where(Metadata.bot_id == bot_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        metadata_list = result.scalars().all()
        logger.debug(f"Number of metadata records fetched: {len(metadata_list)}")
        return metadata_list

    async def create(self, metadata_data: dict, user_id: int) -> Metadata:
        """
        Создать новые метаданные для бота.

        Args:
            metadata_data (dict): Данные для создания новых метаданных.
            user_id (int): ID пользователя, который создаёт метаданные.

        Returns:
            Metadata: Созданный объект Metadata.
        """
        logger.debug(
            f"Creating new metadata for user ID: {user_id} with data: {metadata_data}"
        )
        # Проверка миграций перед созданием метаданных
        try:
            await Metadata.check_migrations_status(self.session)
            logger.debug("Migrations are up-to-date.")
        except MigrationException as e:
            logger.error(f"Migration check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        metadata = Metadata(**metadata_data, user_id=user_id)
        self.session.add(metadata)
        try:
            await self.session.commit()
            await self.session.refresh(metadata)
            logger.info(f"Metadata created successfully: {metadata}")
            return metadata
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating metadata: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create metadata.")

    async def update(self, metadata_id: int, metadata_data: dict) -> Optional[Metadata]:
        """
        Обновить метаданные по их ID.

        Args:
            metadata_id (int): ID метаданных для обновления.
            metadata_data (dict): Данные для обновления.

        Returns:
            Metadata | None: Обновленный объект Metadata, если найден, иначе None.
        """
        logger.debug(
            f"Updating metadata ID: {metadata_id} with data: {metadata_data}"
        )
        # Проверка миграций перед обновлением метаданных
        try:
            await Metadata.check_migrations_status(self.session)
            logger.debug("Migrations are up-to-date.")
        except MigrationException as e:
            logger.error(f"Migration check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        query = (
            update(Metadata)
            .where(Metadata.id == metadata_id)
            .values(**metadata_data)
            .returning(Metadata)
        )
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            updated_metadata = result.scalar_one_or_none()
            if updated_metadata:
                logger.info(f"Metadata updated successfully: {updated_metadata}")
            else:
                logger.warning(f"No metadata found with ID: {metadata_id} to update.")
            return updated_metadata
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating metadata: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update metadata.")

    async def delete(self, metadata_id: int) -> bool:
        """
        Удалить метаданные по их ID.

        Args:
            metadata_id (int): ID метаданных для удаления.

        Returns:
            bool: True, если метаданные были удалены, иначе False.
        """
        logger.debug(f"Deleting metadata with ID: {metadata_id}")
        # Проверка миграций перед удалением метаданных
        try:
            await Metadata.check_migrations_status(self.session)
            logger.debug("Migrations are up-to-date.")
        except MigrationException as e:
            logger.error(f"Migration check failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        query = delete(Metadata).where(Metadata.id == metadata_id)
        try:
            result = await self.session.execute(query)
            await self.session.commit()
            if result.rowcount > 0:
                logger.info(f"Metadata with ID {metadata_id} deleted successfully.")
                return True
            else:
                logger.warning(f"No metadata found with ID: {metadata_id} to delete.")
                return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting metadata: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete metadata.")
