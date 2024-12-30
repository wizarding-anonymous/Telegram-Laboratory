from typing import List

from fastapi import HTTPException, Depends, Query
from loguru import logger

from src.api.schemas.message_schema import (
    TextMessageCreate,
    TextMessageUpdate,
    TextMessageResponse,
)
from src.api.schemas.response_schema import PaginatedResponse, SuccessResponse
from src.core.utils import handle_exceptions, validate_bot_id, validate_content, validate_block_ids
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.core.utils.exceptions import BlockNotFoundException
from src.integrations.logging_client import LoggingClient
from src.db.repositories.bot_repository import BotRepository

logging_client = LoggingClient(service_name="bot_constructor")


class MessageController:
    """
    Controller for handling message-related operations.
    """

    def __init__(self, 
                 block_repository: BlockRepository = Depends(),
                 bot_repository: BotRepository = Depends()
                 ):
        self.block_repository = block_repository
        self.bot_repository = bot_repository

    @handle_exceptions
    async def create_text_message_block(
        self,
        message_create: TextMessageCreate,
        user: dict = Depends(get_current_user),
    ) -> TextMessageResponse:
        """Creates a new text message block."""
        logging_client.info(f"Creating new text message block for bot {message_create.bot_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create text message blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        validate_bot_id(message_create.bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(message_create.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {message_create.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")


        validate_content(message_create.content)

        block = await self.block_repository.create(
            message_create.model_dump(), type="text_message"
        )
        logging_client.info(f"Text message block created successfully with ID: {block.id}")

        return TextMessageResponse(**block.model_dump())

    @handle_exceptions
    async def get_text_message_block(
        self,
        block_id: int,
         user: dict = Depends(get_current_user),
    ) -> TextMessageResponse:
            """Get a text message block."""
            logging_client.info(f"Getting text message block with ID: {block_id}")

            if "admin" not in user.get("roles", []):
                 logging_client.warning(f"User: {user['id']} does not have permission to get text message blocks")
                 raise HTTPException(status_code=403, detail="Permission denied")

            validate_block_ids([block_id])

            block = await self.block_repository.get_by_id(block_id)

            if not block:
                logging_client.error(f"Text message block with id {block_id} not found.")
                raise BlockNotFoundException(block_id=block_id)

            # Verify bot ownership
            bot = await self.bot_repository.get_by_id(block.bot_id)
            if not bot or bot.user_id != user["id"]:
               logging_client.warning(f"User with id: {user['id']} not authorized to access block with id: {block_id}")
               raise HTTPException(status_code=403, detail="Not authorized to access this block")


            logging_client.info(f"Text message block retrieved successfully with ID: {block.id}")

            return TextMessageResponse(**block.model_dump())

    @handle_exceptions
    async def get_all_text_message_blocks(
        self,
        bot_id: int,
        user: dict = Depends(get_current_user),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
    ) -> PaginatedResponse[TextMessageResponse]:
        """Gets all text messages for a bot."""
        
        logging_client.info(f"Getting all text message blocks for bot ID: {bot_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to get text message blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        validate_bot_id(bot_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot or bot.user_id != user["id"]:
             logging_client.warning(f"User with id: {user['id']} not authorized to access bot with id: {bot_id}")
             raise HTTPException(status_code=403, detail="Not authorized to access this bot")


        blocks, total = await self.block_repository.list_paginated(
           page=page, page_size=page_size, bot_id=bot_id, type="text_message"
        )

        if not blocks:
          logging_client.warning(f"No text message blocks found for bot ID: {bot_id}")
          return PaginatedResponse(items=[], page=page, page_size=page_size, total=0)

        text_messages = [TextMessageResponse(**block.model_dump()) for block in blocks]

        logging_client.info(f"Text message blocks retrieved successfully, count: {len(blocks)}")

        return PaginatedResponse(
            items=text_messages, page=page, page_size=page_size, total=total
        )

    @handle_exceptions
    async def update_text_message_block(
        self,
        block_id: int,
        text_message: TextMessageUpdate,
        user: dict = Depends(get_current_user),
    ) -> TextMessageResponse:
        """Updates an existing text message block."""

        logging_client.info(f"Updating text message block with ID: {block_id}")
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update text message blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        validate_block_ids([block_id])

        block = await self.block_repository.get_by_id(block_id)
        
        if not block:
            logging_client.error(f"Text message block with id {block_id} not found.")
            raise BlockNotFoundException(block_id=block_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")


        validate_content(text_message.content)

        updated_block = await self.block_repository.update(
            block_id=block_id,
            content=text_message.model_dump(exclude_unset=True),
        )
        
        if not updated_block:
            logging_client.warning(f"Text message block with id {block_id} not found after update")
            raise BlockNotFoundException(block_id=block_id)

        logging_client.info(f"Text message block updated successfully with ID: {updated_block.id}")

        return TextMessageResponse(**updated_block.model_dump())

    @handle_exceptions
    async def delete_text_message_block(
        self,
        block_id: int,
         user: dict = Depends(get_current_user),
    ) -> SuccessResponse:
        """Deletes a text message block."""
        logging_client.info(f"Deleting text message block with ID: {block_id}")
        
        if "admin" not in user.get("roles", []):
           logging_client.warning(f"User with id: {user['id']} does not have permission to delete text message blocks")
           raise HTTPException(status_code=403, detail="Permission denied")

        validate_block_ids([block_id])

        block = await self.block_repository.get_by_id(block_id)

        if not block:
            logging_client.error(f"Text message block with id {block_id} not found.")
            raise BlockNotFoundException(block_id=block_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to delete block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")


        await self.block_repository.delete(block_id=block_id)

        logging_client.info(f"Text message block deleted successfully with ID: {block_id}")

        return SuccessResponse(message="Text message block deleted successfully")

    @handle_exceptions
    async def save_message_id(self, block_id: int, message_id: int, user: dict = Depends(get_current_user)) -> SuccessResponse:
        """Saves message id."""
        logging_client.info(f"Saving message id: {message_id} for block {block_id}")

        if "admin" not in user.get("roles", []):
           logging_client.warning(f"User with id: {user['id']} does not have permission to save message ids")
           raise HTTPException(status_code=403, detail="Permission denied")

        validate_block_ids([block_id])

        block = await self.block_repository.get_by_id(block_id)

        if not block:
           logging_client.error(f"Text message block with id {block_id} not found.")
           raise BlockNotFoundException(block_id=block_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")

        await self.block_repository.update(block_id, {"user_message_id": message_id})

        logging_client.info(f"Message id: {message_id} saved for block: {block_id}")
        return SuccessResponse(message="Message id saved successfully")
    
    @handle_exceptions
    async def save_bot_message_id(self, block_id: int, message_id: int, user: dict = Depends(get_current_user)) -> SuccessResponse:
        """Saves bot message id."""
        logging_client.info(f"Saving bot message id: {message_id} for block {block_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to save bot message ids")
            raise HTTPException(status_code=403, detail="Permission denied")
       
        validate_block_ids([block_id])

        block = await self.block_repository.get_by_id(block_id)

        if not block:
           logging_client.error(f"Text message block with id {block_id} not found.")
           raise BlockNotFoundException(block_id=block_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
             logging_client.warning(f"User with id: {user['id']} not authorized to modify block with id: {block_id}")
             raise HTTPException(status_code=403, detail="Not authorized to modify this block")

        await self.block_repository.update(block_id, {"bot_message_id": message_id})

        logging_client.info(f"Bot message id: {message_id} saved for block: {block_id}")
        return SuccessResponse(message="Bot message id saved successfully")