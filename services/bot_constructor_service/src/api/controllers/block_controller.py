"""Block Controller module for managing bot logic blocks."""

from typing import List, Optional, Dict
from fastapi import HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.repositories.block_repository import BlockRepository
from src.db.repositories.bot_repository import BotRepository
from src.api.schemas.block_schema import (
    BlockCreate,
    BlockUpdate,
    BlockResponse,
    BlockConnection,
    TextMessageCreate,
    TextMessageUpdate,
    TextMessageResponse,
    KeyboardCreate,
    KeyboardUpdate,
    KeyboardResponse,
    CallbackCreate,
    CallbackUpdate,
    CallbackResponse,
    ApiRequestCreate,
    ApiRequestUpdate,
    ApiRequestResponse,
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
)
from src.api.schemas.response_schema import SuccessResponse, ErrorResponse, PaginatedResponse
from src.integrations.auth_service import get_current_user
from src.core.logic_manager import LogicManager
from src.core.utils import handle_exceptions, validate_block_type, validate_content, validate_bot_id, validate_block_ids, validate_connections
from src.core.utils.exceptions import BlockNotFoundException, InvalidBlockTypeException, InvalidBotIdException
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class BlockController:
    """Controller for managing bot logic blocks."""

    def __init__(self,
                 session: AsyncSession = Depends(get_session),
                 block_repository: BlockRepository = Depends(),
                 bot_repository: BotRepository = Depends(),
                 logic_manager: LogicManager = Depends()
                 ):
        """Initialize block controller."""
        self.session = session
        self.block_repository = block_repository
        self.bot_repository = bot_repository
        self.logic_manager = logic_manager

    @handle_exceptions
    async def create_block(self, block_create: BlockCreate, user: dict = Depends(get_current_user)) -> BlockResponse:
        """Create new logic block."""
        logging_client.info(f"Creating new block of type: {block_create.type} for bot {block_create.bot_id}")
         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate bot_id
        validate_bot_id(block_create.bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block_create.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {block_create.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")

        # Validate block type and content
        validate_block_type(block_create.type)
        if block_create.content:
           validate_content(block_create.content)
        
        # Create the block
        block = await self.block_repository.create(block_create.model_dump())
        
        # Initialize the block in the logic manager
        await self.logic_manager.initialize_block(block)
        
        logging_client.info(f"Successfully created block {block.id} of type: {block.type} for bot {block_create.bot_id}")
        return BlockResponse(**block.model_dump())

    @handle_exceptions
    async def get_bot_blocks(
        self,
        bot_id: int,
        user: dict = Depends(get_current_user),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
    ) -> PaginatedResponse[BlockResponse]:
        """Get all blocks for a bot."""
        logging_client.info(f"Fetching blocks for bot {bot_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to get blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate bot_id
        validate_bot_id(bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to get blocks of bot with id: {bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this bot")
        
        blocks, total = await self.block_repository.list_paginated(
            page=page, page_size=page_size, bot_id=bot_id
        )
        block_list = [BlockResponse(**block.model_dump()) for block in blocks]
        logging_client.info(f"Found {len(block_list)} blocks for bot {bot_id}")
        return PaginatedResponse(
          items=block_list, page=page, page_size=page_size, total=total
         )

    @handle_exceptions
    async def get_block(self, block_id: int, user: dict = Depends(get_current_user)) -> BlockResponse:
        """Get block by ID."""
        logging_client.info(f"Fetching block {block_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to get blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise BlockNotFoundException(block_id=block_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
             logging_client.warning(f"User with id: {user['id']} not authorized to access block with id: {block_id}")
             raise HTTPException(status_code=403, detail="Not authorized to access this block")
        
        logging_client.info(f"Successfully retrieved block {block_id}")
        return BlockResponse(**block.model_dump())

    @handle_exceptions
    async def update_block(self, block_id: int, block_update: BlockUpdate, user: dict = Depends(get_current_user)) -> BlockResponse:
        """Update existing block."""
        logging_client.info(f"Updating block {block_id}")
         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
           logging_client.warning(f"Block with id: {block_id} not found")
           raise BlockNotFoundException(block_id=block_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
           logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
           raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        # Validate updated block type and content
        if block_update.type:
            validate_block_type(block_update.type)
        if block_update.content:
            validate_content(block_update.content)
        
        # Update the block
        updated_block = await self.block_repository.update(
            block_id,
            block_update.model_dump(exclude_unset=True)
        )
        
        if not updated_block:
            logging_client.warning(f"Block with id: {block_id} not found after update")
            raise BlockNotFoundException(block_id=block_id)

        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Successfully updated block {block_id}")
        return BlockResponse(**updated_block.model_dump())

    @handle_exceptions
    async def delete_block(self, block_id: int, user: dict = Depends(get_current_user)) -> SuccessResponse:
        """Delete block by ID."""
        logging_client.info(f"Deleting block {block_id}")
         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to delete blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
           logging_client.warning(f"Block with id: {block_id} not found")
           raise BlockNotFoundException(block_id=block_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
             logging_client.warning(f"User with id: {user['id']} not authorized to delete block with id: {block_id}")
             raise HTTPException(status_code=403, detail="Not authorized to delete this block")
        
        # Remove block from logic manager
        await self.logic_manager.remove_block(block_id)
        
        # Delete block
        deleted = await self.block_repository.delete(block_id)
        if not deleted:
           logging_client.warning(f"Block with id: {block_id} not found or already deleted")
           raise BlockNotFoundException(block_id=block_id)
        
        logging_client.info(f"Successfully deleted block {block_id}")
        return SuccessResponse(message="Block deleted successfully")

    @handle_exceptions
    async def create_connection(self, connection: BlockConnection, user: dict = Depends(get_current_user)) -> SuccessResponse:
        """Create connection between blocks."""
        logging_client.info(
            f"Creating connection between blocks {connection.source_block_id} "
            f"and {connection.target_block_id}"
        )
         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create block connections")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate block IDs
        validate_block_ids([connection.source_block_id, connection.target_block_id])

        # Verify blocks exist
        source_block = await self.block_repository.get_by_id(connection.source_block_id)
        target_block = await self.block_repository.get_by_id(connection.target_block_id)
        
        if not source_block or not target_block:
             logging_client.warning(f"One or both blocks with id: {connection.source_block_id}, {connection.target_block_id} not found")
             raise HTTPException(status_code=404, detail="One or both blocks not found")
        
        # Verify blocks belong to the same bot
        if source_block.bot_id != target_block.bot_id:
            logging_client.warning(f"Blocks must belong to the same bot")
            raise HTTPException(status_code=400, detail="Blocks must belong to the same bot")
        
        bot = await self.bot_repository.get_by_id(source_block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify these blocks")
            raise HTTPException(status_code=403, detail="Not authorized to modify these blocks")
        
        validate_connections(connection.source_block_id, connection.target_block_id)
        # Create connection in logic manager
        await self.logic_manager.connect_blocks(
            connection.source_block_id,
            connection.target_block_id
        )
        
        # Update blocks with connection information
        await self.block_repository.add_connection(
            connection.source_block_id,
            connection.target_block_id
        )
        
        logging_client.info(f"Successfully created connection between blocks {connection.source_block_id} and {connection.target_block_id}")
        return SuccessResponse(message="Connection created successfully")
    
    @handle_exceptions
    async def create_text_message_block(self, message_create: TextMessageCreate, user: dict = Depends(get_current_user)) -> TextMessageResponse:
         """Create new text message block."""
         logging_client.info(f"Creating new text message block for bot {message_create.bot_id}")
          # Validate user permissions
         if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user['id']} does not have permission to create text message blocks")
             raise HTTPException(status_code=403, detail="Permission denied")

         # Validate bot_id
         validate_bot_id(message_create.bot_id)
        
        # Verify bot ownership
         bot = await self.bot_repository.get_by_id(message_create.bot_id)
         if not bot or bot.user_id != user["id"]:
             logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {message_create.bot_id}")
             raise HTTPException(status_code=403, detail="Not authorized to modify this bot")
         
         # Validate content
         if message_create.content:
             validate_content(message_create.content)
        
         # Create the block
         block = await self.block_repository.create(message_create.model_dump(), type="text_message")
        
         # Initialize the block in the logic manager
         await self.logic_manager.initialize_block(block)
        
         logging_client.info(f"Successfully created text message block {block.id} for bot {message_create.bot_id}")
         return TextMessageResponse(**block.model_dump())

    @handle_exceptions
    async def update_text_message_block(self, block_id: int, message_update: TextMessageUpdate, user: dict = Depends(get_current_user)) -> TextMessageResponse:
        """Update existing text message block."""
        logging_client.info(f"Updating text message block {block_id}")
         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update text message blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate block_id
        validate_block_ids([block_id])
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise BlockNotFoundException(block_id=block_id)

         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")

        # Validate  content
        if message_update.content:
            validate_content(message_update.content)
        
        # Update the block
        updated_block = await self.block_repository.update(
            block_id,
            message_update.model_dump(exclude_unset=True)
        )
        
        if not updated_block:
           logging_client.warning(f"Block with id: {block_id} not found after update")
           raise BlockNotFoundException(block_id=block_id)
        
        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Successfully updated text message block {block_id}")
        return TextMessageResponse(**updated_block.model_dump())

    @handle_exceptions
    async def create_keyboard_block(self, keyboard_create: KeyboardCreate, user: dict = Depends(get_current_user)) -> KeyboardResponse:
        """Create new keyboard block."""
        logging_client.info(f"Creating new keyboard block for bot {keyboard_create.bot_id}")

         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create keyboard blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate bot_id
        validate_bot_id(keyboard_create.bot_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(keyboard_create.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {keyboard_create.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")

        # Create the block
        block = await self.block_repository.create(keyboard_create.model_dump(), type="keyboard")

         # Initialize the block in the logic manager
        await self.logic_manager.initialize_block(block)
        
        logging_client.info(f"Successfully created keyboard block {block.id} for bot {keyboard_create.bot_id}")
        return KeyboardResponse(**block.model_dump())

    @handle_exceptions
    async def update_keyboard_block(self, block_id: int, keyboard_update: KeyboardUpdate, user: dict = Depends(get_current_user)) -> KeyboardResponse:
        """Update existing keyboard block."""
        logging_client.info(f"Updating keyboard block {block_id}")
          # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update keyboard blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise BlockNotFoundException(block_id=block_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        # Update the block
        updated_block = await self.block_repository.update(
            block_id,
            keyboard_update.model_dump(exclude_unset=True)
        )
        
        if not updated_block:
            logging_client.warning(f"Block with id: {block_id} not found after update")
            raise BlockNotFoundException(block_id=block_id)

        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Successfully updated keyboard block {block_id}")
        return KeyboardResponse(**updated_block.model_dump())

    @handle_exceptions
    async def create_callback_block(self, callback_create: CallbackCreate, user: dict = Depends(get_current_user)) -> CallbackResponse:
        """Create new callback block."""
        logging_client.info(f"Creating new callback block for bot {callback_create.bot_id}")

          # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create callback blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate bot_id
        validate_bot_id(callback_create.bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(callback_create.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {callback_create.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")
        
        # Create the block
        block = await self.block_repository.create(callback_create.model_dump(), type="callback")
         # Initialize the block in the logic manager
        await self.logic_manager.initialize_block(block)
        
        logging_client.info(f"Successfully created callback block {block.id} for bot {callback_create.bot_id}")
        return CallbackResponse(**block.model_dump())

    @handle_exceptions
    async def update_callback_block(self, block_id: int, callback_update: CallbackUpdate, user: dict = Depends(get_current_user)) -> CallbackResponse:
        """Update existing callback block."""
        logging_client.info(f"Updating callback block {block_id}")
          # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update callback blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise BlockNotFoundException(block_id=block_id)

        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        # Update the block
        updated_block = await self.block_repository.update(
            block_id,
            callback_update.model_dump(exclude_unset=True)
        )

        if not updated_block:
            logging_client.warning(f"Block with id: {block_id} not found after update")
            raise BlockNotFoundException(block_id=block_id)
        
        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Successfully updated callback block {block_id}")
        return CallbackResponse(**updated_block.model_dump())

    @handle_exceptions
    async def create_api_request_block(self, api_request_create: ApiRequestCreate, user: dict = Depends(get_current_user)) -> ApiRequestResponse:
        """Create new api request block."""
        logging_client.info(f"Creating new api request block for bot {api_request_create.bot_id}")
         # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create api request blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate bot_id
        validate_bot_id(api_request_create.bot_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(api_request_create.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {api_request_create.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")

        # Create the block
        block = await self.block_repository.create(api_request_create.model_dump(), type="api_request")
        
         # Initialize the block in the logic manager
        await self.logic_manager.initialize_block(block)
        
        logging_client.info(f"Successfully created api request block {block.id} for bot {api_request_create.bot_id}")
        return ApiRequestResponse(**block.model_dump())

    @handle_exceptions
    async def update_api_request_block(self, block_id: int, api_request_update: ApiRequestUpdate, user: dict = Depends(get_current_user)) -> ApiRequestResponse:
        """Update existing api request block."""
        logging_client.info(f"Updating api request block {block_id}")
          # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update api request blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
             logging_client.warning(f"Block with id: {block_id} not found")
             raise BlockNotFoundException(block_id=block_id)

        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        # Update the block
        updated_block = await self.block_repository.update(
            block_id,
            api_request_update.model_dump(exclude_unset=True)
        )
        
        if not updated_block:
             logging_client.warning(f"Block with id: {block_id} not found after update")
             raise BlockNotFoundException(block_id=block_id)
        
         # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Successfully updated api request block {block_id}")
        return ApiRequestResponse(**updated_block.model_dump())
    
    @handle_exceptions
    async def create_webhook_block(self, webhook_create: WebhookCreate, user: dict = Depends(get_current_user)) -> WebhookResponse:
         """Create new webhook block."""
         logging_client.info(f"Creating new webhook block for bot {webhook_create.bot_id}")
          # Validate user permissions
         if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create webhook blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Validate bot_id
         validate_bot_id(webhook_create.bot_id)
        
         # Verify bot ownership
         bot = await self.bot_repository.get_by_id(webhook_create.bot_id)
         if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {webhook_create.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")
         
         # Validate content
         if webhook_create.url:
             validate_content(webhook_create.url)

         # Create the block
         block = await self.block_repository.create(webhook_create.model_dump(), type="webhook")
        
         # Initialize the block in the logic manager
         await self.logic_manager.initialize_block(block)
        
         logging_client.info(f"Successfully created webhook block {block.id} for bot {webhook_create.bot_id}")
         return WebhookResponse(**block.model_dump())

    @handle_exceptions
    async def update_webhook_block(self, block_id: int, webhook_update: WebhookUpdate, user: dict = Depends(get_current_user)) -> WebhookResponse:
        """Update existing webhook block."""
        logging_client.info(f"Updating webhook block {block_id}")
           # Validate user permissions
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to update webhook blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
             logging_client.warning(f"Block with id: {block_id} not found")
             raise BlockNotFoundException(block_id=block_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        # Validate  content
        if webhook_update.url:
             validate_content(webhook_update.url)

        # Update the block
        updated_block = await self.block_repository.update(
            block_id,
            webhook_update.model_dump(exclude_unset=True)
        )
        
        if not updated_block:
            logging_client.warning(f"Block with id: {block_id} not found after update")
            raise BlockNotFoundException(block_id=block_id)

        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Successfully updated webhook block {block_id}")
        return WebhookResponse(**updated_block.model_dump())