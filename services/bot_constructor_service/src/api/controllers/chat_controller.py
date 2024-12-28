from typing import List

from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.chat_schema import (
    ChatMemberCreate,
    ChatMemberResponse,
    ChatMemberListResponse,
    ChatTitleUpdate,
    ChatDescriptionUpdate,
    ChatMessagePinUpdate,
    ChatMessageUnpinUpdate,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_chat_id, validate_user_id, validate_content
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class ChatController:
    """
    Controller for handling chat-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_chat_member(
        self,
        bot_id: int,
        chat_member: ChatMemberCreate,
        current_user: User = Depends(get_current_user),
    ) -> ChatMemberResponse:
        """Creates a new chat member block."""

        validate_bot_id(bot_id)
        validate_chat_id(chat_member.chat_id)
        validate_user_id(chat_member.user_id)
        logger.info(f"Creating new chat member block for bot ID: {bot_id}, chat ID: {chat_member.chat_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="chat_member",
            content={
              "chat_id": chat_member.chat_id,
              "user_id": chat_member.user_id,
            },
           user_id=current_user.id,
        )
        logger.info(f"Chat member block created successfully with ID: {block.id}")
        return ChatMemberResponse(
            id=block.id,
            type=block.type,
            chat_id=block.content["chat_id"],
            user_id=block.content["user_id"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )


    @handle_exceptions
    async def get_chat_member(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> ChatMemberResponse:
        """Get a chat member block."""
        
        logger.info(f"Getting chat member block with ID: {block_id}")
        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="chat_member"
        )

        if not block:
            logger.error(f"Chat member block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        logger.info(f"Chat member block retrieved successfully with ID: {block.id}")
        return ChatMemberResponse(
            id=block.id,
            type=block.type,
            chat_id=block.content["chat_id"],
            user_id=block.content["user_id"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_all_chat_members(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> ChatMemberListResponse:
        """Gets all chat member blocks for a bot."""
        
        validate_bot_id(bot_id)
        logger.info(f"Getting all chat member blocks for bot ID: {bot_id}")

        blocks = await self.block_repository.get_all(
             bot_id=bot_id, user_id=current_user.id, type="chat_member"
        )

        if not blocks:
            logger.warning(f"No chat member blocks found for bot ID: {bot_id}")
            return ChatMemberListResponse(items=[])

        logger.info(f"Chat member blocks retrieved successfully, count: {len(blocks)}")

        return ChatMemberListResponse(
            items=[
                ChatMemberResponse(
                    id=block.id,
                    type=block.type,
                    chat_id=block.content["chat_id"],
                    user_id=block.content["user_id"],
                    created_at=block.created_at,
                    updated_at=block.updated_at,
                )
                for block in blocks
            ]
        )

    @handle_exceptions
    async def update_chat_member(
        self,
        block_id: int,
        chat_member: ChatMemberCreate,
         current_user: User = Depends(get_current_user),
    ) -> ChatMemberResponse:
            """Updates an existing chat member block."""

            validate_chat_id(chat_member.chat_id)
            validate_user_id(chat_member.user_id)
            logger.info(f"Updating chat member block with ID: {block_id}")

            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="chat_member"
            )

            if not block:
                logger.error(f"Chat member block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            updated_block = await self.block_repository.update(
                block_id=block_id,
                content={
                    "chat_id": chat_member.chat_id,
                    "user_id": chat_member.user_id,
                },
            )
            
            logger.info(f"Chat member block updated successfully with ID: {updated_block.id}")

            return ChatMemberResponse(
                id=updated_block.id,
                type=updated_block.type,
                chat_id=updated_block.content["chat_id"],
                user_id=updated_block.content["user_id"],
                created_at=updated_block.created_at,
                updated_at=updated_block.updated_at,
            )

    @handle_exceptions
    async def delete_chat_member(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
            """Deletes a chat member block."""
            logger.info(f"Deleting chat member block with ID: {block_id}")

            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="chat_member"
            )

            if not block:
                logger.error(f"Chat member block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            await self.block_repository.delete(block_id=block_id)
            logger.info(f"Chat member block deleted successfully with ID: {block_id}")
    

    @handle_exceptions
    async def update_chat_title(
        self,
        bot_id: int,
        chat_title: ChatTitleUpdate,
        current_user: User = Depends(get_current_user),
    ) -> None:
         """Updates a chat title."""
         validate_bot_id(bot_id)
         validate_chat_id(chat_title.chat_id)
         validate_content(chat_title.title)

         logger.info(f"Updating chat title for bot ID: {bot_id}, chat ID: {chat_title.chat_id}")
         
         block = await self.block_repository.create(
           bot_id=bot_id,
           type="chat_title",
           content={
               "chat_id": chat_title.chat_id,
               "title": chat_title.title
           },
            user_id=current_user.id,
         )
         
         if not block:
            logger.error(f"Chat title block with id {block.id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
         
         logger.info(f"Chat title updated successfully for block ID: {block.id}")


    @handle_exceptions
    async def update_chat_description(
        self,
        bot_id: int,
        chat_description: ChatDescriptionUpdate,
         current_user: User = Depends(get_current_user),
    ) -> None:
        """Updates a chat description."""

        validate_bot_id(bot_id)
        validate_chat_id(chat_description.chat_id)
        validate_content(chat_description.description)
        
        logger.info(f"Updating chat description for bot ID: {bot_id}, chat ID: {chat_description.chat_id}")
        
        block = await self.block_repository.create(
             bot_id=bot_id,
             type="chat_description",
             content={
               "chat_id": chat_description.chat_id,
               "description": chat_description.description
            },
            user_id=current_user.id,
         )

        if not block:
             logger.error(f"Chat description block with id {block.id} not found.")
             raise HTTPException(status_code=404, detail="Block not found")
        
        logger.info(f"Chat description updated successfully for block ID: {block.id}")
    

    @handle_exceptions
    async def update_chat_message_pin(
         self,
         bot_id: int,
         message_pin: ChatMessagePinUpdate,
         current_user: User = Depends(get_current_user),
    ) -> None:
        """Pins a message in the chat."""

        validate_bot_id(bot_id)
        validate_chat_id(message_pin.chat_id)

        logger.info(f"Pinning message for bot ID: {bot_id}, chat ID: {message_pin.chat_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="chat_pin_message",
            content={
                "chat_id": message_pin.chat_id,
                "message_id": message_pin.message_id,
            },
           user_id=current_user.id,
         )

        if not block:
           logger.error(f"Chat pin message block with id {block.id} not found.")
           raise HTTPException(status_code=404, detail="Block not found")
        
        logger.info(f"Message pinned successfully for block ID: {block.id}")

    @handle_exceptions
    async def update_chat_message_unpin(
        self,
        bot_id: int,
        message_unpin: ChatMessageUnpinUpdate,
         current_user: User = Depends(get_current_user),
    ) -> None:
            """Unpins a message in the chat."""
            
            validate_bot_id(bot_id)
            validate_chat_id(message_unpin.chat_id)
            logger.info(f"Unpinning message for bot ID: {bot_id}, chat ID: {message_unpin.chat_id}")

            block = await self.block_repository.create(
                 bot_id=bot_id,
                 type="chat_unpin_message",
                 content={
                    "chat_id": message_unpin.chat_id,
                    "message_id": message_unpin.message_id,
                },
                user_id=current_user.id,
            )

            if not block:
                logger.error(f"Chat unpin message block with id {block.id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")
            
            logger.info(f"Message unpinned successfully for block ID: {block.id}")