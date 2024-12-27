"""Block Controller module for managing bot logic blocks."""

from typing import List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.repositories.block_repository import BlockRepository
from src.db.repositories.bot_repository import BotRepository
from src.api.schemas.block_schema import (
    BlockCreate, 
    BlockUpdate, 
    BlockResponse,
    BlockConnection
)
from src.api.schemas.response_schema import SuccessResponse, ErrorResponse  # Добавлен импорт SuccessResponse
from src.integrations.auth_service import AuthService
from src.core.logic_manager import LogicManager
from src.core.utils import handle_exceptions, validate_block_type, validate_content, validate_bot_id, validate_block_ids  # Исправлен импорт validate_block_id на validate_block_ids

class BlockController:
    """Controller for managing bot logic blocks."""

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """Initialize block controller.
        
        Args:
            session: AsyncSession - Database session
        """
        self.session = session
        self.block_repository = BlockRepository(session)
        self.bot_repository = BotRepository(session)
        self.auth_service = AuthService()
        self.logic_manager = LogicManager()

    @handle_exceptions
    async def create_block(self, block_data: BlockCreate, user_id: int) -> BlockResponse:
        """Create new logic block."""
        logger.info(f"Creating new block for bot {block_data.bot_id}")
        
        # Validate user permissions
        await self.auth_service.validate_user_permissions(user_id, "create_block")
        
        # Validate bot_id
        validate_bot_id(block_data.bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block_data.bot_id)
        if not bot or bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")

        # Validate block type and content
        validate_block_type(block_data.type)  # Обновлено: теперь валидируется только тип
        validate_content(block_data.content)   # Добавлено: валидируем содержимое
        
        # Create the block
        block = await self.block_repository.create(block_data.dict())
        
        # Initialize the block in the logic manager
        await self.logic_manager.initialize_block(block)
        
        logger.info(f"Successfully created block {block.id} for bot {block_data.bot_id}")
        return BlockResponse.from_orm(block)

    @handle_exceptions
    async def get_bot_blocks(
        self, 
        bot_id: int, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[BlockResponse]:
        """Get all blocks for a bot."""
        logger.info(f"Fetching blocks for bot {bot_id}")
        
        # Validate permissions
        await self.auth_service.validate_user_permissions(user_id, "read_block")
        
        # Validate bot_id
        validate_bot_id(bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot or bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this bot")
        
        blocks = await self.block_repository.get_all_by_bot(bot_id, skip, limit)
        return [BlockResponse.from_orm(block) for block in blocks]

    @handle_exceptions
    async def get_block(self, block_id: int, user_id: int) -> BlockResponse:
        """Get block by ID."""
        logger.info(f"Fetching block {block_id}")
        
        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Validate permissions
        await self.auth_service.validate_user_permissions(user_id, "read_block")
        
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this block")
            
        return BlockResponse.from_orm(block)

    @handle_exceptions
    async def update_block(self, block_id: int, block_data: BlockUpdate, user_id: int) -> BlockResponse:
        """Update existing block."""
        logger.info(f"Updating block {block_id}")
        
        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Validate permissions
        await self.auth_service.validate_user_permissions(user_id, "update_block")
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        # Validate updated block type and content
        if block_data.type:
            validate_block_type(block_data.type)  # Обновлено: теперь валидируется только тип
        if block_data.content:
            validate_content(block_data.content)  # Добавлено: валидируем содержимое
        
        # Update the block
        updated_block = await self.block_repository.update(
            block_id, 
            block_data.dict(exclude_unset=True)
        )
        
        if not updated_block:
            raise HTTPException(status_code=404, detail="Block not found after update")
        
        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logger.info(f"Successfully updated block {block_id}")
        return BlockResponse.from_orm(updated_block)

    @handle_exceptions
    async def delete_block(self, block_id: int, user_id: int) -> SuccessResponse:
        """Delete block by ID."""
        logger.info(f"Deleting block {block_id}")
        
        # Validate block_id
        validate_block_ids([block_id])  # Используем validate_block_ids для одного ID
        
        # Validate permissions
        await self.auth_service.validate_user_permissions(user_id, "delete_block")
        
        # Verify block exists
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this block")

        # Remove block from logic manager
        await self.logic_manager.remove_block(block_id)
        
        # Delete block
        deleted = await self.block_repository.delete(block_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Block not found or already deleted")
        
        logger.info(f"Successfully deleted block {block_id}")
        return SuccessResponse(message="Block deleted successfully")

    @handle_exceptions
    async def create_connection(self, connection: BlockConnection, user_id: int) -> SuccessResponse:
        """Create connection between blocks."""
        logger.info(
            f"Creating connection between blocks {connection.source_block_id} "
            f"and {connection.target_block_id}"
        )
        
        # Validate permissions
        await self.auth_service.validate_user_permissions(user_id, "update_block")
        
        # Validate block IDs
        validate_block_ids([connection.source_block_id, connection.target_block_id])
        
        # Verify blocks exist
        source_block = await self.block_repository.get_by_id(connection.source_block_id)
        target_block = await self.block_repository.get_by_id(connection.target_block_id)
        
        if not source_block or not target_block:
            raise HTTPException(status_code=404, detail="One or both blocks not found")
        
        # Verify blocks belong to the same bot
        if source_block.bot_id != target_block.bot_id:
            raise HTTPException(status_code=400, detail="Blocks must belong to the same bot")
            
        bot = await self.bot_repository.get_by_id(source_block.bot_id)
        if not bot or bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify these blocks")

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
        
        logger.info("Successfully created connection between blocks")
        return SuccessResponse(message="Connection created successfully")
