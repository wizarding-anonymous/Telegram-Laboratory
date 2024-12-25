# services/bot_constructor_service/src/api/controllers/bot_controller.py
"""Bot Controller module for managing Telegram bots."""

from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.repositories.bot_repository import BotRepository
from src.api.schemas.bot_schema import BotCreate, BotUpdate, BotResponse
from src.integrations.auth_service import AuthService
from src.core.logic_manager import LogicManager
from src.core.utils import handle_exceptions, validate_bot_name, validate_bot_id
from src.api.schemas.response_schema import SuccessResponse

class BotController:
    """Controller for managing bot operations."""

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """Initialize bot controller with database session.
        
        Args:
            session: AsyncSession - Database session
        """
        self.session = session
        self.repository = BotRepository(session)
        self.auth_service = AuthService()
        self.logic_manager = LogicManager()

    @handle_exceptions
    async def create_bot(self, bot_data: BotCreate, user_id: int) -> BotResponse:
        """Create new bot for user."""
        logger.info(f"Creating new bot for user {user_id}")
        
        # Validate user permissions
        await self.auth_service.validate_user_permissions(user_id, "create_bot")
        
        # Validate bot name
        validate_bot_name(bot_data.name)
        
        # Create bot
        bot = await self.repository.create(bot_data.dict(), user_id)
        
        # Initialize bot in logic manager if necessary
        await self.logic_manager.initialize_bot(bot)
        
        logger.info(f"Successfully created bot {bot.id}")
        return BotResponse.from_orm(bot)

    @handle_exceptions
    async def get_bot(self, bot_id: int, user_id: int) -> BotResponse:
        """Get bot by ID."""
        logger.info(f"Fetching bot {bot_id}")
        
        # Validate bot ID
        validate_bot_id(bot_id)
        
        # Check permissions
        await self.auth_service.validate_user_permissions(user_id, "read_bot")
        
        bot = await self.repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
            
        if bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this bot")
            
        return BotResponse.from_orm(bot)

    @handle_exceptions
    async def get_user_bots(self, user_id: int, skip: int = 0, limit: int = 100) -> List[BotResponse]:
        """Get all bots for user with pagination."""
        logger.info(f"Fetching bots for user {user_id}")
        
        # Validate user permissions
        await self.auth_service.validate_user_permissions(user_id, "read_bot")
        
        bots = await self.repository.get_all_by_user(user_id, skip, limit)
        return [BotResponse.from_orm(bot) for bot in bots]

    @handle_exceptions
    async def update_bot(self, bot_id: int, bot_data: BotUpdate, user_id: int) -> BotResponse:
        """Update existing bot."""
        logger.info(f"Updating bot {bot_id}")
        
        # Validate bot ID
        validate_bot_id(bot_id)
        
        # Check permissions
        await self.auth_service.validate_user_permissions(user_id, "update_bot")
        
        # Verify bot exists and belongs to user
        bot = await self.repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
            
        if bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this bot")
        
        # Validate updated bot name if provided
        if bot_data.name:
            validate_bot_name(bot_data.name)
        
        # Update bot
        updated_bot = await self.repository.update(bot_id, bot_data.dict(exclude_unset=True))
        if not updated_bot:
            raise HTTPException(status_code=404, detail="Bot not found after update")
        
        # Update bot in logic manager
        await self.logic_manager.update_bot(updated_bot)
        
        logger.info(f"Successfully updated bot {bot_id}")
        
        return BotResponse.from_orm(updated_bot)

    @handle_exceptions
    async def delete_bot(self, bot_id: int, user_id: int) -> SuccessResponse:
        """Delete bot by ID."""
        logger.info(f"Deleting bot {bot_id}")
        
        # Validate bot ID
        validate_bot_id(bot_id)
        
        # Check permissions
        await self.auth_service.validate_user_permissions(user_id, "delete_bot")
        
        # Verify bot exists and belongs to user
        bot = await self.repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
            
        if bot.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this bot")
        
        # Remove bot from logic manager if necessary
        await self.logic_manager.remove_bot(bot_id)
        
        # Delete bot
        deleted = await self.repository.delete(bot_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Bot not found or already deleted")
        
        logger.info(f"Successfully deleted bot {bot_id}")
        
        return SuccessResponse(message="Bot deleted successfully")
