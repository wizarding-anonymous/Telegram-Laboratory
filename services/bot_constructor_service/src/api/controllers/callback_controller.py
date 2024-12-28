from typing import List

from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.callback_schema import (
    CallbackQueryCreate,
    CallbackQueryUpdate,
    CallbackQueryResponse,
    CallbackQueryListResponse,
    CallbackResponseCreate,
    CallbackResponseUpdate,
    CallbackResponseResponse,
    CallbackResponseListResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_content, validate_block_ids
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class CallbackController:
    """
    Controller for handling callback-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_callback_query(
        self,
        bot_id: int,
        callback_query: CallbackQueryCreate,
        current_user: User = Depends(get_current_user),
    ) -> CallbackQueryResponse:
        """Creates a new callback query handler block."""

        validate_bot_id(bot_id)
        logger.info(f"Creating new callback query handler for bot ID: {bot_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="callback_query_handler",
            content={"data": callback_query.data},
            user_id=current_user.id,
        )

        logger.info(f"Callback query handler created successfully with ID: {block.id}")

        return CallbackQueryResponse(
            id=block.id,
            type=block.type,
            data=block.content["data"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_callback_query(
            self,
            block_id: int,
            current_user: User = Depends(get_current_user),
    ) -> CallbackQueryResponse:
            """Get a callback query handler block."""

            logger.info(f"Getting callback query handler with ID: {block_id}")

            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="callback_query_handler"
            )

            if not block:
                logger.error(f"Callback query handler with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")
            
            logger.info(f"Callback query handler retrieved successfully with ID: {block.id}")
            return CallbackQueryResponse(
                id=block.id,
                type=block.type,
                data=block.content["data"],
                created_at=block.created_at,
                updated_at=block.updated_at,
            )

    @handle_exceptions
    async def get_all_callback_queries(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> CallbackQueryListResponse:
        """Gets all callback query handlers for a bot."""

        validate_bot_id(bot_id)
        logger.info(f"Getting all callback query handler blocks for bot ID: {bot_id}")

        blocks = await self.block_repository.get_all(
            bot_id=bot_id, user_id=current_user.id, type="callback_query_handler"
        )
        if not blocks:
            logger.warning(f"No callback query handler blocks found for bot ID: {bot_id}")
            return CallbackQueryListResponse(items=[])
        
        logger.info(f"Callback query handler blocks retrieved successfully, count: {len(blocks)}")

        return CallbackQueryListResponse(
            items=[
                CallbackQueryResponse(
                    id=block.id,
                    type=block.type,
                    data=block.content["data"],
                    created_at=block.created_at,
                    updated_at=block.updated_at,
                )
                for block in blocks
            ]
        )

    @handle_exceptions
    async def update_callback_query(
        self,
        block_id: int,
        callback_query: CallbackQueryUpdate,
         current_user: User = Depends(get_current_user),
    ) -> CallbackQueryResponse:
            """Updates an existing callback query handler block."""

            logger.info(f"Updating callback query handler with ID: {block_id}")

            block = await self.block_repository.get(
               block_id=block_id, user_id=current_user.id, type="callback_query_handler"
            )

            if not block:
                logger.error(f"Callback query handler with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            updated_block = await self.block_repository.update(
                block_id=block_id,
                content={"data": callback_query.data},
            )

            logger.info(f"Callback query handler updated successfully with ID: {updated_block.id}")
            return CallbackQueryResponse(
                 id=updated_block.id,
                type=updated_block.type,
                data=updated_block.content["data"],
                created_at=updated_block.created_at,
                updated_at=updated_block.updated_at,
            )

    @handle_exceptions
    async def delete_callback_query(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
        """Deletes a callback query handler block."""

        logger.info(f"Deleting callback query handler with ID: {block_id}")

        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="callback_query_handler"
        )
        
        if not block:
            logger.error(f"Callback query handler with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        await self.block_repository.delete(block_id=block_id)
        logger.info(f"Callback query handler deleted successfully with ID: {block_id}")

    @handle_exceptions
    async def create_callback_response(
        self,
        bot_id: int,
        callback_response: CallbackResponseCreate,
        current_user: User = Depends(get_current_user),
    ) -> CallbackResponseResponse:
            """Creates a new callback response block."""

            validate_bot_id(bot_id)
            logger.info(f"Creating new callback response for bot ID: {bot_id}")

            block = await self.block_repository.create(
                bot_id=bot_id,
                type="callback_response",
                content={"text": callback_response.text},
                user_id=current_user.id,
            )

            logger.info(f"Callback response block created successfully with ID: {block.id}")
            return CallbackResponseResponse(
                id=block.id,
                type=block.type,
                text=block.content["text"],
                created_at=block.created_at,
                updated_at=block.updated_at,
            )

    @handle_exceptions
    async def get_callback_response(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> CallbackResponseResponse:
            """Get a callback response block."""
            logger.info(f"Getting callback response block with ID: {block_id}")

            block = await self.block_repository.get(
               block_id=block_id, user_id=current_user.id, type="callback_response"
            )

            if not block:
                logger.error(f"Callback response block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            logger.info(f"Callback response block retrieved successfully with ID: {block.id}")
            return CallbackResponseResponse(
                 id=block.id,
                type=block.type,
                text=block.content["text"],
                created_at=block.created_at,
                updated_at=block.updated_at,
            )

    @handle_exceptions
    async def get_all_callback_responses(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> CallbackResponseListResponse:
            """Gets all callback response blocks for a bot."""
            
            validate_bot_id(bot_id)
            logger.info(f"Getting all callback response blocks for bot ID: {bot_id}")
            
            blocks = await self.block_repository.get_all(
                 bot_id=bot_id, user_id=current_user.id, type="callback_response"
            )

            if not blocks:
              logger.warning(f"No callback response blocks found for bot ID: {bot_id}")
              return CallbackResponseListResponse(items=[])

            logger.info(f"Callback response blocks retrieved successfully, count: {len(blocks)}")
            return CallbackResponseListResponse(
                items=[
                    CallbackResponseResponse(
                         id=block.id,
                         type=block.type,
                         text=block.content["text"],
                         created_at=block.created_at,
                         updated_at=block.updated_at,
                    )
                    for block in blocks
                ]
            )

    @handle_exceptions
    async def update_callback_response(
        self,
        block_id: int,
        callback_response: CallbackResponseUpdate,
        current_user: User = Depends(get_current_user),
    ) -> CallbackResponseResponse:
            """Updates an existing callback response block."""
            logger.info(f"Updating callback response block with ID: {block_id}")

            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="callback_response"
            )
            
            if not block:
                logger.error(f"Callback response block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            updated_block = await self.block_repository.update(
                block_id=block_id,
                content={"text": callback_response.text},
            )

            logger.info(f"Callback response block updated successfully with ID: {updated_block.id}")

            return CallbackResponseResponse(
                 id=updated_block.id,
                type=updated_block.type,
                text=updated_block.content["text"],
                created_at=updated_block.created_at,
                updated_at=updated_block.updated_at,
            )

    @handle_exceptions
    async def delete_callback_response(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
            """Deletes a callback response block."""
            
            logger.info(f"Deleting callback response block with ID: {block_id}")

            block = await self.block_repository.get(
               block_id=block_id, user_id=current_user.id, type="callback_response"
            )
            if not block:
                logger.error(f"Callback response block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            await self.block_repository.delete(block_id=block_id)

            logger.info(f"Callback response block deleted successfully with ID: {block_id}")

    @handle_exceptions
    async def connect_callback(
        self,
        block_id: int,
        connections: List[int],
         current_user: User = Depends(get_current_user),
    ):
            """Connects a callback block to other blocks."""
            validate_block_ids(connections)
            logger.info(f"Connecting callback block with ID: {block_id} to blocks: {connections}")

            block = await self.block_repository.get(
                 block_id=block_id, user_id=current_user.id, type__in=["callback_query_handler", "callback_response"]
            )

            if not block:
                 logger.error(f"Callback block with id {block_id} not found.")
                 raise HTTPException(status_code=404, detail="Block not found")
            
            await self.block_repository.connect_blocks(block_id=block_id, connections=connections)
            logger.info(f"Callback block with id {block_id} connected to blocks: {connections}")