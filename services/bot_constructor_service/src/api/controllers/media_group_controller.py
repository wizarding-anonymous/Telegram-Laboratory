from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    MediaGroupCreate,
    MediaGroupUpdate,
    MediaGroupResponse,
    MediaGroupListResponse,
    ErrorResponse,
    SuccessResponse,
)
from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import BlockRepository
from src.integrations import get_current_user
from src.core.utils import validate_bot_id, validate_block_ids
from src.core.utils.exceptions import BotNotFoundException
from src.config import settings
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class MediaGroupController:
    """
    Controller for handling media group block operations.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.block_repository = BlockRepository(session)

    @handle_exceptions
    async def create_media_group(
        self, bot_id: int, media_group: MediaGroupCreate, user: dict = Depends(get_current_user)
    ) -> MediaGroupResponse:
        """Creates a new media group block."""
        logging_client.info(f"Creating media group block for bot with id: {bot_id}")
        validate_bot_id(bot_id)

        if "admin" not in user.get("roles", []):
            logging_client.warning(
                f"User with id: {user.get('id')} has not admin rights"
            )
            raise HTTPException(status_code=403, detail="Admin role required")

        bot = await self.block_repository.get_bot_by_id(bot_id)
        if not bot:
           logging_client.warning(f"Bot with id {bot_id} was not found")
           raise BotNotFoundException(bot_id=bot_id)

        new_block = await self.block_repository.create(
            bot_id=bot_id, type="media_group", content=media_group.model_dump()
        )
        logging_client.info(f"Media group block with id: {new_block.id} for bot with id: {bot_id} created successfully")
        return MediaGroupResponse(**new_block.model_dump())


    @handle_exceptions
    async def get_media_group(
        self, block_id: int, user: dict = Depends(get_current_user)
    ) -> MediaGroupResponse:
        """Retrieves a media group block by ID."""
        logging_client.info(f"Getting media group block with id: {block_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(
                f"User with id: {user.get('id')} has not admin rights"
            )
            raise HTTPException(status_code=403, detail="Admin role required")

        block = await self.block_repository.get_by_id(block_id)
        if not block or block.type != "media_group":
            logging_client.warning(f"Media group block with id: {block_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media group block not found"
            )
        logging_client.info(f"Media group block with id: {block_id} was retrieved successfully")
        return MediaGroupResponse(**block.model_dump())
    
    @handle_exceptions
    async def get_all_media_groups(
        self, bot_id: int, user: dict = Depends(get_current_user)
    ) -> MediaGroupListResponse:
        """Retrieves all media group blocks by bot id."""
        logging_client.info(f"Getting all media group blocks for bot with id: {bot_id}")
        validate_bot_id(bot_id)

        if "admin" not in user.get("roles", []):
           logging_client.warning(
                f"User with id: {user.get('id')} has not admin rights"
           )
           raise HTTPException(status_code=403, detail="Admin role required")

        blocks = await self.block_repository.get_by_bot_id_and_type(bot_id, "media_group")
        
        media_group_responses = [
            MediaGroupResponse(**block.model_dump())
            for block in blocks
        ]
        logging_client.info(f"Media group blocks for bot with id: {bot_id} retrieved successfully")
        return MediaGroupListResponse(items=media_group_responses)

    @handle_exceptions
    async def update_media_group(
        self,
        block_id: int,
        media_group: MediaGroupUpdate,
        user: dict = Depends(get_current_user)
    ) -> MediaGroupResponse:
        """Updates an existing media group block."""
        logging_client.info(f"Updating media group block with id: {block_id}")

        if "admin" not in user.get("roles", []):
           logging_client.warning(
                f"User with id: {user.get('id')} has not admin rights"
           )
           raise HTTPException(status_code=403, detail="Admin role required")
        
        block = await self.block_repository.get_by_id(block_id)
        if not block or block.type != "media_group":
             logging_client.warning(f"Media group block with id: {block_id} not found")
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media group block not found"
            )
        
        updated_block = await self.block_repository.update(
             block_id, content=media_group.model_dump(exclude_unset=True)
        )
        logging_client.info(f"Media group block with id: {block_id} was updated successfully")
        return MediaGroupResponse(**updated_block.model_dump())

    @handle_exceptions
    async def delete_media_group(
        self, block_id: int, user: dict = Depends(get_current_user)
    ) -> SuccessResponse:
        """Deletes a media group block by its ID."""
        logging_client.info(f"Deleting media group block with id: {block_id}")

        if "admin" not in user.get("roles", []):
           logging_client.warning(
                f"User with id: {user.get('id')} has not admin rights"
           )
           raise HTTPException(status_code=403, detail="Admin role required")

        block = await self.block_repository.get_by_id(block_id)
        if not block or block.type != "media_group":
            logging_client.warning(f"Media group block with id: {block_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media group block not found"
            )
        await self.block_repository.delete(block_id)
        logging_client.info(f"Media group block with id: {block_id} was deleted successfully")
        return SuccessResponse(message="Media group block deleted successfully")