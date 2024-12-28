from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.variable_schema import (
    VariableCreate,
    VariableUpdate,
    VariableResponse,
    VariableListResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_content
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class VariableController:
    """
    Controller for handling variable-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_variable(
        self,
        bot_id: int,
        variable: VariableCreate,
        current_user: User = Depends(get_current_user),
    ) -> VariableResponse:
        """Creates a new variable block."""
        validate_bot_id(bot_id)
        validate_content(variable.name)
        logger.info(f"Creating new variable block for bot ID: {bot_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="variable",
            content={"name": variable.name, "value": variable.value},
            user_id=current_user.id,
        )

        logger.info(f"Variable block created successfully with ID: {block.id}")
        return VariableResponse(
            id=block.id,
            type=block.type,
            name=block.content["name"],
            value=block.content["value"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
    
    @handle_exceptions
    async def get_variable(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> VariableResponse:
        """Get a variable block."""

        logger.info(f"Getting variable block with ID: {block_id}")
        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="variable"
        )

        if not block:
            logger.error(f"Variable block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
        
        logger.info(f"Variable block retrieved successfully with ID: {block.id}")

        return VariableResponse(
            id=block.id,
            type=block.type,
            name=block.content["name"],
            value=block.content["value"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
    
    @handle_exceptions
    async def get_all_variables(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> VariableListResponse:
        """Gets all variable blocks for a bot."""
        
        validate_bot_id(bot_id)
        logger.info(f"Getting all variable blocks for bot ID: {bot_id}")
        blocks = await self.block_repository.get_all(
             bot_id=bot_id, user_id=current_user.id, type="variable"
        )
        if not blocks:
            logger.warning(f"No variable blocks found for bot ID: {bot_id}")
            return VariableListResponse(items=[])

        logger.info(f"Variable blocks retrieved successfully, count: {len(blocks)}")
        
        return VariableListResponse(
            items=[
               VariableResponse(
                    id=block.id,
                    type=block.type,
                    name=block.content["name"],
                    value=block.content["value"],
                    created_at=block.created_at,
                    updated_at=block.updated_at,
               )
               for block in blocks
            ]
        )
    
    @handle_exceptions
    async def update_variable(
        self,
        block_id: int,
        variable: VariableUpdate,
         current_user: User = Depends(get_current_user),
    ) -> VariableResponse:
        """Updates an existing variable block."""

        logger.info(f"Updating variable block with ID: {block_id}")
        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="variable"
        )

        if not block:
            logger.error(f"Variable block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        updated_block = await self.block_repository.update(
            block_id=block_id,
            content={"name": variable.name, "value": variable.value},
        )
        logger.info(f"Variable block updated successfully with ID: {updated_block.id}")
        return VariableResponse(
             id=updated_block.id,
             type=updated_block.type,
             name=updated_block.content["name"],
             value=updated_block.content["value"],
             created_at=updated_block.created_at,
             updated_at=updated_block.updated_at,
        )

    @handle_exceptions
    async def delete_variable(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
        """Deletes a variable block."""
        logger.info(f"Deleting variable block with ID: {block_id}")

        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="variable"
        )
        if not block:
            logger.error(f"Variable block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        await self.block_repository.delete(block_id=block_id)
        logger.info(f"Variable block deleted successfully with ID: {block_id}")