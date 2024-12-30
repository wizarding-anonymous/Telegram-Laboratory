from typing import List, Dict

from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.flow_schema import (
    FlowChartCreate,
    FlowChartUpdate,
    FlowChartResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.core.utils import handle_exceptions, validate_bot_id, validate_block_ids
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.core.utils.exceptions import BlockNotFoundException
from src.integrations.logging_client import LoggingClient
from src.db.repositories.bot_repository import BotRepository
from src.core.logic_manager import LogicManager


logging_client = LoggingClient(service_name="bot_constructor")


class FlowController:
    """
    Controller for handling bot flow-related operations.
    """

    def __init__(self, 
                 block_repository: BlockRepository = Depends(),
                 bot_repository: BotRepository = Depends(),
                 logic_manager: LogicManager = Depends()
                 ):
        self.block_repository = block_repository
        self.bot_repository = bot_repository
        self.logic_manager = logic_manager


    @handle_exceptions
    async def create_flow_chart_block(
        self,
        flow_chart: FlowChartCreate,
        user: dict = Depends(get_current_user),
    ) -> FlowChartResponse:
        """Creates a new flow chart for a bot."""
        logging_client.info(f"Creating new flow chart block for bot {flow_chart.bot_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create flow chart blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        validate_bot_id(flow_chart.bot_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(flow_chart.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to modify bot with id: {flow_chart.bot_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this bot")

        block = await self.block_repository.create(
            flow_chart.model_dump(), type="flow_chart"
        )
         # Initialize the block in the logic manager
        await self.logic_manager.initialize_block(block)
        
        logging_client.info(f"Flow chart block created successfully with ID: {block.id}")
        return FlowChartResponse(**block.model_dump())
        
    @handle_exceptions
    async def get_flow_chart_block(
        self, block_id: int,  user: dict = Depends(get_current_user)
    ) -> FlowChartResponse:
        """Get a flow chart block by ID."""
        
        logging_client.info(f"Getting flow chart block with ID: {block_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to get flow chart blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        validate_block_ids([block_id])
        
        block = await self.block_repository.get_by_id(block_id)
        if not block:
           logging_client.error(f"Flow chart block with id {block_id} not found.")
           raise BlockNotFoundException(block_id=block_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
             logging_client.warning(f"User with id: {user['id']} not authorized to access block with id: {block_id}")
             raise HTTPException(status_code=403, detail="Not authorized to access this block")

        logging_client.info(f"Flow chart block retrieved successfully with ID: {block.id}")

        return FlowChartResponse(**block.model_dump())
        
    @handle_exceptions
    async def update_flow_chart_block(
        self,
        block_id: int,
        flow_chart: FlowChartUpdate,
        user: dict = Depends(get_current_user),
    ) -> FlowChartResponse:
        """Updates an existing flow chart block."""
        logging_client.info(f"Updating flow chart block with ID: {block_id}")
        
        if "admin" not in user.get("roles", []):
           logging_client.warning(f"User with id: {user['id']} does not have permission to update flow chart blocks")
           raise HTTPException(status_code=403, detail="Permission denied")

        validate_block_ids([block_id])
        
        block = await self.block_repository.get_by_id(block_id)

        if not block:
           logging_client.error(f"Flow chart block with id {block_id} not found.")
           raise BlockNotFoundException(block_id=block_id)
        
        # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to update block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")

        updated_block = await self.block_repository.update(
            block_id=block_id,
            content=flow_chart.model_dump(exclude_unset=True),
        )
        
        if not updated_block:
            logging_client.warning(f"Flow chart block with id {block_id} not found after update.")
            raise BlockNotFoundException(block_id=block_id)

        # Update block in logic manager
        await self.logic_manager.update_block(updated_block)
        
        logging_client.info(f"Flow chart block updated successfully with ID: {updated_block.id}")

        return FlowChartResponse(**updated_block.model_dump())
        
    @handle_exceptions
    async def delete_flow_chart_block(
        self, block_id: int,  user: dict = Depends(get_current_user)
    ) -> SuccessResponse:
        """Deletes a flow chart block."""
        
        logging_client.info(f"Deleting flow chart block with ID: {block_id}")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to delete flow chart blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        validate_block_ids([block_id])
        
        block = await self.block_repository.get_by_id(block_id)

        if not block:
            logging_client.error(f"Flow chart block with id {block_id} not found.")
            raise BlockNotFoundException(block_id=block_id)
        
         # Verify bot ownership
        bot = await self.bot_repository.get_by_id(block.bot_id)
        if not bot or bot.user_id != user["id"]:
            logging_client.warning(f"User with id: {user['id']} not authorized to delete block with id: {block_id}")
            raise HTTPException(status_code=403, detail="Not authorized to modify this block")
        
        deleted = await self.block_repository.delete(block_id=block_id)
        
        if not deleted:
            logging_client.warning(f"Flow chart block with id {block_id} not found or already deleted.")
            raise BlockNotFoundException(block_id=block_id)

        # Remove block from logic manager
        await self.logic_manager.remove_block(block_id)
        
        logging_client.info(f"Flow chart block deleted successfully with ID: {block_id}")
        return SuccessResponse(message="Flow chart block deleted successfully")