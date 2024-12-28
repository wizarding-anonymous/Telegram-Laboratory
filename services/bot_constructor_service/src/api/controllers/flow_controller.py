from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.flow_schema import (
    FlowChartCreate,
    FlowChartUpdate,
    FlowChartResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class FlowController:
    """
    Controller for handling bot flow-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_flow_chart(
        self,
        bot_id: int,
        flow_chart: FlowChartCreate,
        current_user: User = Depends(get_current_user),
    ) -> FlowChartResponse:
        """Creates a new flow chart for a bot."""
        validate_bot_id(bot_id)
        logger.info(f"Creating new flow chart for bot ID: {bot_id}")
        
        block = await self.block_repository.create(
            bot_id=bot_id,
            type="flow_chart",
            content={"logic": flow_chart.logic},
            user_id=current_user.id,
        )
        logger.info(f"Flow chart block created successfully with ID: {block.id}")
        return FlowChartResponse(
            id=block.id,
            type=block.type,
            logic=block.content["logic"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
        
    @handle_exceptions
    async def get_flow_chart(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> FlowChartResponse:
        """Get a flow chart block by ID."""
        
        logger.info(f"Getting flow chart block with ID: {block_id}")

        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="flow_chart"
        )
        if not block:
           logger.error(f"Flow chart block with id {block_id} not found.")
           raise HTTPException(status_code=404, detail="Block not found")
        
        logger.info(f"Flow chart block retrieved successfully with ID: {block.id}")

        return FlowChartResponse(
            id=block.id,
            type=block.type,
            logic=block.content["logic"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
        
    @handle_exceptions
    async def update_flow_chart(
        self,
        block_id: int,
        flow_chart: FlowChartUpdate,
        current_user: User = Depends(get_current_user),
    ) -> FlowChartResponse:
        """Updates an existing flow chart block."""

        logger.info(f"Updating flow chart block with ID: {block_id}")

        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="flow_chart"
        )

        if not block:
           logger.error(f"Flow chart block with id {block_id} not found.")
           raise HTTPException(status_code=404, detail="Block not found")

        updated_block = await self.block_repository.update(
            block_id=block_id,
            content={"logic": flow_chart.logic},
        )
        logger.info(f"Flow chart block updated successfully with ID: {updated_block.id}")

        return FlowChartResponse(
             id=updated_block.id,
             type=updated_block.type,
             logic=updated_block.content["logic"],
             created_at=updated_block.created_at,
             updated_at=updated_block.updated_at,
        )
        
    @handle_exceptions
    async def delete_flow_chart(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
        """Deletes a flow chart block."""
        
        logger.info(f"Deleting flow chart block with ID: {block_id}")

        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="flow_chart"
        )

        if not block:
            logger.error(f"Flow chart block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
        
        await self.block_repository.delete(block_id=block_id)
        logger.info(f"Flow chart block deleted successfully with ID: {block_id}")