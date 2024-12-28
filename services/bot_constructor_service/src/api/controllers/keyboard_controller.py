from typing import List

from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.keyboard_schema import (
    ReplyKeyboardCreate,
    ReplyKeyboardUpdate,
    ReplyKeyboardResponse,
    ReplyKeyboardListResponse,
    InlineKeyboardCreate,
    InlineKeyboardUpdate,
    InlineKeyboardResponse,
    InlineKeyboardListResponse,
    KeyboardButtonSchema,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_block_ids
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class KeyboardController:
    """
    Controller for handling keyboard-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_reply_keyboard(
        self,
        bot_id: int,
        keyboard: ReplyKeyboardCreate,
        current_user: User = Depends(get_current_user),
    ) -> ReplyKeyboardResponse:
        """Creates a new reply keyboard block."""

        validate_bot_id(bot_id)
        logger.info(f"Creating new reply keyboard for bot ID: {bot_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="reply_keyboard",
            content={"buttons": [button.dict() for button in keyboard.buttons]},
            user_id=current_user.id,
        )

        logger.info(f"Reply keyboard block created successfully with ID: {block.id}")
        return ReplyKeyboardResponse(
            id=block.id,
            type=block.type,
            buttons=[KeyboardButtonSchema(**button) for button in block.content["buttons"]],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_reply_keyboard(
        self, block_id: int, current_user: User = Depends(get_current_user)
    ) -> ReplyKeyboardResponse:
        """Get a reply keyboard block."""

        logger.info(f"Getting reply keyboard block with ID: {block_id}")
        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="reply_keyboard"
        )

        if not block:
            logger.error(f"Reply keyboard block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        logger.info(f"Reply keyboard block retrieved successfully with ID: {block.id}")

        return ReplyKeyboardResponse(
            id=block.id,
            type=block.type,
            buttons=[KeyboardButtonSchema(**button) for button in block.content["buttons"]],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_all_reply_keyboards(
        self, bot_id: int, current_user: User = Depends(get_current_user)
    ) -> ReplyKeyboardListResponse:
        """Gets all reply keyboards for a bot."""

        validate_bot_id(bot_id)
        logger.info(f"Getting all reply keyboard blocks for bot ID: {bot_id}")

        blocks = await self.block_repository.get_all(
            bot_id=bot_id, user_id=current_user.id, type="reply_keyboard"
        )

        if not blocks:
            logger.warning(f"No reply keyboard blocks found for bot ID: {bot_id}")
            return ReplyKeyboardListResponse(items=[])
        
        logger.info(f"Reply keyboard blocks retrieved successfully, count: {len(blocks)}")
        return ReplyKeyboardListResponse(
            items=[
                ReplyKeyboardResponse(
                    id=block.id,
                    type=block.type,
                    buttons=[KeyboardButtonSchema(**button) for button in block.content["buttons"]],
                    created_at=block.created_at,
                    updated_at=block.updated_at,
                )
                for block in blocks
            ]
        )

    @handle_exceptions
    async def update_reply_keyboard(
        self,
        block_id: int,
        keyboard: ReplyKeyboardUpdate,
         current_user: User = Depends(get_current_user),
    ) -> ReplyKeyboardResponse:
        """Updates an existing reply keyboard block."""

        logger.info(f"Updating reply keyboard block with ID: {block_id}")
        
        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="reply_keyboard"
        )

        if not block:
          logger.error(f"Reply keyboard block with id {block_id} not found.")
          raise HTTPException(status_code=404, detail="Block not found")

        updated_block = await self.block_repository.update(
            block_id=block_id,
            content={"buttons": [button.dict() for button in keyboard.buttons]},
        )

        logger.info(f"Reply keyboard block updated successfully with ID: {updated_block.id}")

        return ReplyKeyboardResponse(
            id=updated_block.id,
            type=updated_block.type,
            buttons=[KeyboardButtonSchema(**button) for button in updated_block.content["buttons"]],
            created_at=updated_block.created_at,
            updated_at=updated_block.updated_at,
        )

    @handle_exceptions
    async def delete_reply_keyboard(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
        """Deletes a reply keyboard block."""

        logger.info(f"Deleting reply keyboard block with ID: {block_id}")

        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="reply_keyboard"
        )
        if not block:
            logger.error(f"Reply keyboard block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        await self.block_repository.delete(block_id=block_id)

        logger.info(f"Reply keyboard block deleted successfully with ID: {block_id}")

    @handle_exceptions
    async def create_inline_keyboard(
        self,
        bot_id: int,
        keyboard: InlineKeyboardCreate,
          current_user: User = Depends(get_current_user),
    ) -> InlineKeyboardResponse:
        """Creates a new inline keyboard block."""

        validate_bot_id(bot_id)
        logger.info(f"Creating new inline keyboard for bot ID: {bot_id}")
        
        block = await self.block_repository.create(
            bot_id=bot_id,
            type="inline_keyboard",
            content={"buttons": [button.dict() for button in keyboard.buttons]},
            user_id=current_user.id,
        )

        logger.info(f"Inline keyboard block created successfully with ID: {block.id}")
        return InlineKeyboardResponse(
             id=block.id,
             type=block.type,
             buttons=[KeyboardButtonSchema(**button) for button in block.content["buttons"]],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
    
    @handle_exceptions
    async def get_inline_keyboard(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> InlineKeyboardResponse:
        """Get an inline keyboard block."""

        logger.info(f"Getting inline keyboard block with ID: {block_id}")
        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="inline_keyboard"
        )

        if not block:
            logger.error(f"Inline keyboard block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
        
        logger.info(f"Inline keyboard block retrieved successfully with ID: {block.id}")
        return InlineKeyboardResponse(
            id=block.id,
            type=block.type,
            buttons=[KeyboardButtonSchema(**button) for button in block.content["buttons"]],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
    
    @handle_exceptions
    async def get_all_inline_keyboards(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> InlineKeyboardListResponse:
            """Gets all inline keyboards for a bot."""

            validate_bot_id(bot_id)
            logger.info(f"Getting all inline keyboard blocks for bot ID: {bot_id}")

            blocks = await self.block_repository.get_all(
                bot_id=bot_id, user_id=current_user.id, type="inline_keyboard"
            )

            if not blocks:
               logger.warning(f"No inline keyboard blocks found for bot ID: {bot_id}")
               return InlineKeyboardListResponse(items=[])

            logger.info(f"Inline keyboard blocks retrieved successfully, count: {len(blocks)}")
            
            return InlineKeyboardListResponse(
                items=[
                    InlineKeyboardResponse(
                      id=block.id,
                      type=block.type,
                      buttons=[KeyboardButtonSchema(**button) for button in block.content["buttons"]],
                      created_at=block.created_at,
                      updated_at=block.updated_at,
                    )
                    for block in blocks
                ]
            )

    @handle_exceptions
    async def update_inline_keyboard(
        self,
        block_id: int,
        keyboard: InlineKeyboardUpdate,
        current_user: User = Depends(get_current_user),
    ) -> InlineKeyboardResponse:
            """Updates an existing inline keyboard block."""
            logger.info(f"Updating inline keyboard block with ID: {block_id}")

            block = await self.block_repository.get(
               block_id=block_id, user_id=current_user.id, type="inline_keyboard"
            )
            
            if not block:
                logger.error(f"Inline keyboard block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            updated_block = await self.block_repository.update(
                block_id=block_id,
                content={"buttons": [button.dict() for button in keyboard.buttons]},
            )

            logger.info(f"Inline keyboard block updated successfully with ID: {updated_block.id}")
            return InlineKeyboardResponse(
                id=updated_block.id,
                type=updated_block.type,
                buttons=[KeyboardButtonSchema(**button) for button in updated_block.content["buttons"]],
                created_at=updated_block.created_at,
                updated_at=updated_block.updated_at,
            )

    @handle_exceptions
    async def delete_inline_keyboard(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
        """Deletes an inline keyboard block."""

        logger.info(f"Deleting inline keyboard block with ID: {block_id}")

        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="inline_keyboard"
        )
        if not block:
            logger.error(f"Inline keyboard block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        await self.block_repository.delete(block_id=block_id)

        logger.info(f"Inline keyboard block deleted successfully with ID: {block_id}")
    
    @handle_exceptions
    async def connect_keyboard(
        self,
        block_id: int,
        connections: List[int],
         current_user: User = Depends(get_current_user),
    ):
            """Connects a keyboard block to other blocks."""

            validate_block_ids(connections)
            logger.info(f"Connecting keyboard block with ID: {block_id} to blocks: {connections}")

            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type__in=["reply_keyboard", "inline_keyboard"]
            )

            if not block:
                logger.error(f"Keyboard block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            await self.block_repository.connect_blocks(block_id=block_id, connections=connections)

            logger.info(f"Keyboard block with id {block_id} connected to blocks: {connections}")