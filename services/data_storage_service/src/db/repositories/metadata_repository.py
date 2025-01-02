from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

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
        metadata = Metadata(**metadata_data)
        self.session.add(metadata)
        await self.session.commit()
        await self.session.refresh(metadata)
        return metadata

    @handle_exceptions
    async def get(self, metadata_id: int) -> Optional[Metadata]:
        """
        Retrieves metadata by its ID.
        """
        query = select(Metadata).where(Metadata.id == metadata_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    @handle_exceptions
    async def update(self, metadata_id: int, **metadata_data) -> Optional[Metadata]:
        """
        Updates metadata by its ID.
        """
        query = select(Metadata).where(Metadata.id == metadata_id)
        result = await self.session.execute(query)
        metadata = result.scalar_one_or_none()
        if metadata:
            for key, value in metadata_data.items():
                setattr(metadata, key, value)
            await self.session.commit()
            await self.session.refresh(metadata)
        return metadata

    @handle_exceptions
    async def delete(self, metadata_id: int) -> None:
        """
        Deletes metadata by its ID.
        """
        query = delete(Metadata).where(Metadata.id == metadata_id)
        await self.session.execute(query)
        await self.session.commit()