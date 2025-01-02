from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.repositories import MetadataRepository
from src.api.schemas import (
    MetadataCreate,
    MetadataResponse,
    MetadataUpdate,
    SuccessResponse,
    ErrorResponse
)
from src.core.utils import handle_exceptions
from src.integrations.auth_service.client import get_current_user


class MetadataController:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.repository = MetadataRepository(session)

    @handle_exceptions
    async def create_metadata(self, metadata_data: MetadataCreate, current_user: dict = Depends(get_current_user)) -> MetadataResponse:
        """
        Creates new metadata for a bot.
        """
        metadata = await self.repository.create(**metadata_data.model_dump())
        return MetadataResponse(**metadata.__dict__)

    @handle_exceptions
    async def get_metadata(self, metadata_id: int, current_user: dict = Depends(get_current_user)) -> MetadataResponse:
        """
        Retrieves metadata by its ID.
        """
        metadata = await self.repository.get(metadata_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata with ID {metadata_id} not found",
            )
        return MetadataResponse(**metadata.__dict__)

    @handle_exceptions
    async def update_metadata(self, metadata_id: int, metadata_data: MetadataUpdate, current_user: dict = Depends(get_current_user)) -> MetadataResponse:
        """
        Updates existing metadata by its ID.
        """
        metadata = await self.repository.get(metadata_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata with ID {metadata_id} not found",
            )
        updated_metadata = await self.repository.update(metadata_id, **metadata_data.model_dump(exclude_unset=True))
        return MetadataResponse(**updated_metadata.__dict__)


    @handle_exceptions
    async def delete_metadata(self, metadata_id: int, current_user: dict = Depends(get_current_user)) -> SuccessResponse:
        """
        Deletes metadata by its ID.
        """
        metadata = await self.repository.get(metadata_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata with ID {metadata_id} not found",
            )
        await self.repository.delete(metadata_id)
        return SuccessResponse(message="Metadata deleted successfully")