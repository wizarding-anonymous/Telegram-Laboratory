from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.models import Metadata
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException


class MetadataRepository:
    """
    Repository for performing CRUD operations on the Metadata model.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, **metadata_data) -> Metadata:
        """
        Creates new metadata in the database.
        """
        logger.info(f"Creating metadata with data: {metadata_data}")
        try:
            metadata = Metadata(**metadata_data)
            self.session.add(metadata)
            await self.session.commit()
            await self.session.refresh(metadata)
            logger.info(f"Metadata created successfully. Metadata id: {metadata.id}")
            return metadata
        except Exception as e:
            logger.error(f"Error creating metadata: {e}")
            raise DatabaseException(f"Failed to create metadata: {e}") from e

    @handle_exceptions
    async def get(self, metadata_id: int) -> Optional[Metadata]:
        """
        Retrieves metadata by its ID.
        """
        logger.info(f"Getting metadata with ID: {metadata_id}")
        try:
            query = select(Metadata).where(Metadata.id == metadata_id)
            result = await self.session.execute(query)
            metadata = result.scalar_one_or_none()
            if metadata:
                logger.debug(f"Metadata with ID {metadata_id} found.")
            else:
                logger.warning(f"Metadata with ID {metadata_id} not found.")
            return metadata
        except Exception as e:
            logger.error(f"Error getting metadata {metadata_id}: {e}")
            raise DatabaseException(f"Failed to get metadata {metadata_id}: {e}") from e

    @handle_exceptions
    async def update(self, metadata_id: int, **metadata_data) -> Optional[Metadata]:
        """
        Updates metadata by its ID.
        """
        logger.info(f"Updating metadata with ID: {metadata_id}, data: {metadata_data}")
        try:
            query = select(Metadata).where(Metadata.id == metadata_id)
            result = await self.session.execute(query)
            metadata = result.scalar_one_or_none()
            if metadata:
                for key, value in metadata_data.items():
                    setattr(metadata, key, value)
                await self.session.commit()
                await self.session.refresh(metadata)
                logger.info(f"Metadata with ID {metadata_id} updated successfully.")
            else:
                logger.warning(f"Metadata with ID {metadata_id} not found for update.")
            return metadata
        except Exception as e:
           logger.error(f"Error updating metadata {metadata_id}: {e}")
           raise DatabaseException(f"Failed to update metadata {metadata_id}: {e}") from e

    @handle_exceptions
    async def delete(self, metadata_id: int) -> None:
        """
        Deletes metadata by its ID.
        """
        logger.info(f"Deleting metadata with ID: {metadata_id}")
        try:
           query = delete(Metadata).where(Metadata.id == metadata_id)
           await self.session.execute(query)
           await self.session.commit()
           logger.info(f"Metadata with ID {metadata_id} deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting metadata {metadata_id}: {e}")
            raise DatabaseException(f"Failed to delete metadata {metadata_id}: {e}") from e

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Metadata]:
        """
        Retrieves all metadata entries for a specific bot ID.
        """
        logger.info(f"Getting all metadata for bot ID: {bot_id}")
        try:
            query = select(Metadata).where(Metadata.bot_id == bot_id)
            result = await self.session.execute(query)
            metadata_list = list(result.scalars().all())
            logger.debug(f"Found {len(metadata_list)} metadata entries for bot ID {bot_id}")
            return metadata_list
        except Exception as e:
            logger.error(f"Error getting all metadata for bot {bot_id}: {e}")
            raise DatabaseException(f"Failed to get all metadata for bot {bot_id}: {e}") from e