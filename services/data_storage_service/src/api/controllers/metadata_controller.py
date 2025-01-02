from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.repositories import MetadataRepository
from src.api.schemas import (
    MetaCreate,
    MetaResponse,
    MetaUpdate,
    MetaListResponse,
    SuccessResponse,
    ErrorResponse
)
from src.core.utils import handle_exceptions
from src.integrations.auth_service.client import get_current_user


class MetadataController:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.repository = MetadataRepository(session)

    @handle_exceptions
    async def create_metadata(self, metadata_data: MetaCreate, current_user: dict = Depends(get_current_user)) -> MetaResponse:
        """
        Creates new metadata for a bot.
        """
        logger.info(f"Creating metadata with data: {metadata_data}")
        try:
            metadata = await self.repository.create(**metadata_data.model_dump())
            logger.info(f"Metadata created successfully. Metadata: {metadata}")
            return MetaResponse(**metadata.__dict__)
        except Exception as e:
            logger.error(f"Error creating metadata: {e}")
            raise

    @handle_exceptions
    async def get_metadata(self, metadata_id: int, current_user: dict = Depends(get_current_user)) -> MetaResponse:
        """
        Retrieves metadata by its ID.
        """
        logger.info(f"Getting metadata with ID: {metadata_id}")
        try:
           metadata = await self.repository.get(metadata_id)
           if not metadata:
               logger.warning(f"Metadata with ID {metadata_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Metadata with ID {metadata_id} not found",
              )
           logger.info(f"Metadata retrieved successfully. Metadata: {metadata}")
           return MetaResponse(**metadata.__dict__)
        except Exception as e:
            logger.error(f"Error getting metadata {metadata_id}: {e}")
            raise


    @handle_exceptions
    async def update_metadata(self, metadata_id: int, metadata_data: MetaUpdate, current_user: dict = Depends(get_current_user)) -> MetaResponse:
        """
        Updates existing metadata by its ID.
        """
        logger.info(f"Updating metadata with ID: {metadata_id}, data: {metadata_data}")
        try:
           metadata = await self.repository.get(metadata_id)
           if not metadata:
               logger.warning(f"Metadata with ID {metadata_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Metadata with ID {metadata_id} not found",
               )
           updated_metadata = await self.repository.update(metadata_id, **metadata_data.model_dump(exclude_unset=True))
           logger.info(f"Metadata updated successfully. Updated metadata: {updated_metadata}")
           return MetaResponse(**updated_metadata.__dict__)
        except Exception as e:
            logger.error(f"Error updating metadata {metadata_id}: {e}")
            raise

    @handle_exceptions
    async def delete_metadata(self, metadata_id: int, current_user: dict = Depends(get_current_user)) -> SuccessResponse:
        """
        Deletes metadata by its ID.
        """
        logger.info(f"Deleting metadata with ID: {metadata_id}")
        try:
            metadata = await self.repository.get(metadata_id)
            if not metadata:
                logger.warning(f"Metadata with ID {metadata_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Metadata with ID {metadata_id} not found",
                )
            await self.repository.delete(metadata_id)
            logger.info(f"Metadata with ID {metadata_id} deleted successfully")
            return SuccessResponse(message="Metadata deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting metadata {metadata_id}: {e}")
            raise
        
    @handle_exceptions
    async def get_all_metadata_by_bot_id(self, bot_id: int, current_user: dict = Depends(get_current_user)) -> MetaListResponse:
      """
      Retrieves all metadata entries for a specific bot ID.
      """
      logger.info(f"Getting all metadata for bot_id: {bot_id}")
      try:
        metadata_list = await self.repository.get_all_by_bot_id(bot_id)
        logger.info(f"Found {len(metadata_list)} metadata entries for bot_id: {bot_id}")
        return MetaListResponse(items=[MetaResponse(**metadata.__dict__) for metadata in metadata_list])
      except Exception as e:
        logger.error(f"Error getting metadata by bot_id {bot_id}: {e}")
        raise