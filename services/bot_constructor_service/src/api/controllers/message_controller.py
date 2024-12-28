from typing import List

from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.message_schema import (
    TextMessageCreate,
    TextMessageUpdate,
    TextMessageResponse,
    TextMessageListResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_content, validate_block_ids
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class MessageController:
    """
    Controller for handling message-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_text_message(
        self,
        bot_id: int,
        text_message: TextMessageCreate,
        current_user: User = Depends(get_current_user),
    ) -> TextMessageResponse:
        """Creates a new text message block."""

        validate_bot_id(bot_id)
        validate_content(text_message.content)

        logger.info(f"Creating new text message block for bot ID: {bot_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="text_message",
            content={"text": text_message.content},
            user_id=current_user.id,
        )

        logger.info(f"Text message block created successfully with ID: {block.id}")

        return TextMessageResponse(
            id=block.id,
            type=block.type,
            content=block.content["text"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_text_message(
            self,
            block_id: int,
            current_user: User = Depends(get_current_user),
    ) -> TextMessageResponse:
            """Get a text message block."""

            logger.info(f"Getting text message block with ID: {block_id}")

            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="text_message"
            )

            if not block:
               logger.error(f"Text message block with id {block_id} not found.")
               raise HTTPException(status_code=404, detail="Block not found")

            logger.info(f"Text message block retrieved successfully with ID: {block.id}")

            return TextMessageResponse(
                id=block.id,
                type=block.type,
                content=block.content["text"],
                created_at=block.created_at,
                updated_at=block.updated_at,
            )

    @handle_exceptions
    async def get_all_text_messages(
        self,
        bot_id: int,
        current_user: User = Depends(get_current_user),
    ) -> TextMessageListResponse:
        """Gets all text messages for a bot."""
        
        validate_bot_id(bot_id)
        logger.info(f"Getting all text message blocks for bot ID: {bot_id}")


        blocks = await self.block_repository.get_all(
            bot_id=bot_id, user_id=current_user.id, type="text_message"
        )

        if not blocks:
          logger.warning(f"No text message blocks found for bot ID: {bot_id}")
          return TextMessageListResponse(items=[])

        logger.info(f"Text message blocks retrieved successfully, count: {len(blocks)}")

        return TextMessageListResponse(
            items=[
                TextMessageResponse(
                    id=block.id,
                    type=block.type,
                    content=block.content["text"],
                    created_at=block.created_at,
                    updated_at=block.updated_at,
                )
                for block in blocks
            ]
        )

    @handle_exceptions
    async def update_text_message(
        self,
        block_id: int,
        text_message: TextMessageUpdate,
        current_user: User = Depends(get_current_user),
    ) -> TextMessageResponse:
        """Updates an existing text message block."""

        validate_content(text_message.content)
        logger.info(f"Updating text message block with ID: {block_id}")

        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="text_message"
        )
        
        if not block:
          logger.error(f"Text message block with id {block_id} not found.")
          raise HTTPException(status_code=404, detail="Block not found")

        updated_block = await self.block_repository.update(
            block_id=block_id,
            content={"text": text_message.content},
        )

        logger.info(f"Text message block updated successfully with ID: {updated_block.id}")

        return TextMessageResponse(
            id=updated_block.id,
            type=updated_block.type,
            content=updated_block.content["text"],
            created_at=updated_block.created_at,
            updated_at=updated_block.updated_at,
        )

    @handle_exceptions
    async def delete_text_message(
        self,
        block_id: int,
         current_user: User = Depends(get_current_user),
    ) -> None:
        """Deletes a text message block."""

        logger.info(f"Deleting text message block with ID: {block_id}")

        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="text_message"
        )

        if not block:
            logger.error(f"Text message block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        await self.block_repository.delete(block_id=block_id)

        logger.info(f"Text message block deleted successfully with ID: {block_id}")

    @handle_exceptions
    async def connect_text_message(
        self,
        block_id: int,
        connections: List[int],
        current_user: User = Depends(get_current_user),
    ):
            """Connects a text message block to other blocks."""

            validate_block_ids(connections)

            logger.info(f"Connecting text message block with ID: {block_id} to blocks: {connections}")

            block = await self.block_repository.get(
               block_id=block_id, user_id=current_user.id, type="text_message"
            )
            if not block:
                logger.error(f"Text message block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")
            
            await self.block_repository.connect_blocks(block_id=block_id, connections=connections)

            logger.info(f"Text message block with id {block_id} connected to blocks: {connections}")