from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import MediaGroup, Connection
from src.core.utils import handle_exceptions
from src.config import settings
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class MediaGroupRepository:
    """
    Repository for performing database operations on media group blocks.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, bot_id: int, items: List[Dict[str, Any]]) -> MediaGroup:
        """
        Creates a new media group block.

        Args:
            bot_id (int): The ID of the bot to associate the block with.
            items (List[Dict[str, Any]]): The list of media items to store.

        Returns:
            MediaGroup: The created media group block object.
        """
        logging_client.info(f"Creating media group block for bot_id: {bot_id}")
        new_media_group = MediaGroup(bot_id=bot_id, content={"items": items})
        self.session.add(new_media_group)
        await self.session.commit()
        await self.session.refresh(new_media_group)
        logging_client.info(f"Media group block with id {new_media_group.id} created successfully for bot_id: {bot_id}")
        return new_media_group

    @handle_exceptions
    async def get_by_id(self, block_id: int) -> Optional[MediaGroup]:
        """
        Retrieves a media group block by its ID.

        Args:
            block_id (int): The ID of the media group block.

        Returns:
            Optional[MediaGroup]: The media group block object, or None if not found.
        """
        logging_client.info(f"Getting media group block with id: {block_id}")
        media_group = await self.session.get(MediaGroup, block_id)
        if media_group:
            logging_client.info(f"Media group block with id: {block_id} was found")
        else:
            logging_client.warning(f"Media group block with id: {block_id} was not found")
        return media_group

    @handle_exceptions
    async def update(self, block_id: int, items: List[Dict[str, Any]]) -> Optional[MediaGroup]:
        """
        Updates an existing media group block.

        Args:
            block_id (int): The ID of the media group block to update.
            items (List[Dict[str, Any]]): The list of media items to store.

        Returns:
            Optional[MediaGroup]: The updated media group block object, or None if not found.
        """
        logging_client.info(f"Updating media group block with id: {block_id}")
        media_group = await self.session.get(MediaGroup, block_id)
        if not media_group:
            logging_client.warning(f"Media group block with id: {block_id} was not found")
            return None

        media_group.content = {"items": items}
        await self.session.commit()
        await self.session.refresh(media_group)
        logging_client.info(f"Media group block with id: {block_id} was updated successfully")
        return media_group

    @handle_exceptions
    async def delete(self, block_id: int) -> None:
        """
        Deletes a media group block by its ID.

        Args:
            block_id (int): The ID of the media group block to delete.
        """
        logging_client.info(f"Deleting media group block with id: {block_id}")
        media_group = await self.session.get(MediaGroup, block_id)
        if media_group:
            await self.session.delete(media_group)
            await self.session.commit()
            logging_client.info(f"Media group block with id: {block_id} was deleted successfully")
        else:
           logging_client.warning(f"Media group block with id: {block_id} was not found")

    @handle_exceptions
    async def _get_next_blocks(self, block_id: int) -> List[MediaGroup]:
        """
        Get next blocks from database.

        Args:
            block_id (int): The ID of the source block.
        Returns:
            List[Block]: list of next blocks
        """
        logging_client.info(f"Get next block for media group block with id: {block_id}")
        query = select(Connection.target_block_id).where(Connection.source_block_id == block_id)
        result = await self.session.execute(query)
        target_ids = [row[0] for row in result.all()]
        if target_ids:
             next_blocks = await self.session.execute(select(MediaGroup).where(MediaGroup.id.in_(target_ids)))
             return next_blocks.scalars().all()
        else:
            logging_client.info(f"Next blocks were not found for media group block with id: {block_id}")
            return []