from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    MediaGroupCreate,
    MediaGroupUpdate,
    MediaGroupResponse,
    MediaGroupListResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import BlockRepository
from src.integrations import get_current_user
from src.core.utils import validate_bot_id, validate_block_ids


class MediaGroupController:
    """
    Controller for handling media group block operations.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.block_repository = BlockRepository(session)

    @handle_exceptions
    async def create_media_group(
        self, bot_id: int, media_group: MediaGroupCreate, current_user: dict = Depends(get_current_user)
    ) -> MediaGroupResponse:
        """Creates a new media group block."""
        validate_bot_id(bot_id)
        
        block = await self.block_repository.create(
            bot_id=bot_id, type="media_group", content=media_group.model_dump()
        )
        return MediaGroupResponse(
            id=block.id,
            type=block.type,
            items=block.content.get('items', []),
            created_at=block.created_at,
            updated_at=block.updated_at
        )

    @handle_exceptions
    async def get_media_group(
        self, block_id: int, current_user: dict = Depends(get_current_user)
    ) -> MediaGroupResponse:
        """Retrieves a media group block by ID."""
        block = await self.block_repository.get(block_id)
        if block is None or block.type != "media_group":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media group block not found"
            )
        return MediaGroupResponse(
            id=block.id,
            type=block.type,
            items=block.content.get('items', []),
            created_at=block.created_at,
            updated_at=block.updated_at
        )
    
    @handle_exceptions
    async def get_all_media_groups(
        self, bot_id: int, current_user: dict = Depends(get_current_user)
    ) -> MediaGroupListResponse:
        """Retrieves all media group blocks by bot id."""
        validate_bot_id(bot_id)
        blocks = await self.block_repository.get_by_bot_id_and_type(bot_id, "media_group")
        
        media_group_responses = [
            MediaGroupResponse(
                id=block.id,
                type=block.type,
                items=block.content.get('items', []),
                created_at=block.created_at,
                updated_at=block.updated_at,
            )
            for block in blocks
        ]
        return MediaGroupListResponse(items=media_group_responses)



    @handle_exceptions
    async def update_media_group(
        self,
        block_id: int,
        media_group: MediaGroupUpdate,
         current_user: dict = Depends(get_current_user)
    ) -> MediaGroupResponse:
        """Updates an existing media group block."""
        block = await self.block_repository.get(block_id)
        if block is None or block.type != "media_group":
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media group block not found"
            )
        updated_block = await self.block_repository.update(
             block_id, content=media_group.model_dump()
        )
        
        return MediaGroupResponse(
            id=updated_block.id,
            type=updated_block.type,
            items=updated_block.content.get('items', []),
            created_at=updated_block.created_at,
            updated_at=updated_block.updated_at,
        )

    @handle_exceptions
    async def delete_media_group(
        self, block_id: int, current_user: dict = Depends(get_current_user)
    ) -> None:
        """Deletes a media group block by its ID."""
        block = await self.block_repository.get(block_id)
        if block is None or block.type != "media_group":
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media group block not found"
            )
        await self.block_repository.delete(block_id)