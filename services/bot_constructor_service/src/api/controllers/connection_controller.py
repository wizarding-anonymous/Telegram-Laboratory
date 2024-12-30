from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException

from src.api.schemas import (
    SuccessResponse,
)
from src.core.utils import handle_exceptions, validate_block_ids
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.logging_client import LoggingClient
from src.core.utils.exceptions import BotNotFoundException
from src.core.logic_manager.base import LogicManager

logging_client = LoggingClient(service_name="bot_constructor")


class ConnectionController:
    """
    Controller for managing connections between blocks.
    """

    def __init__(
        self,
        block_repository: BlockRepository = Depends(),
          logic_manager: LogicManager = Depends()
    ):
        self.block_repository = block_repository
        self.logic_manager = logic_manager

    @handle_exceptions
    async def create_connection(
        self,
        source_block_id: int,
        target_block_id: int,
        user: dict = Depends(get_current_user),
         bot_logic: Dict[str, Any] = None
    ) -> SuccessResponse:
        """Creates a connection between two blocks."""
        logging_client.info(
            f"Creating connection from block id: {source_block_id} to block id: {target_block_id}"
        )
        
        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user.get('id')} does not have permission to create block connections")
             raise HTTPException(status_code=403, detail="Permission denied")
        
        validate_block_ids([source_block_id, target_block_id])
        
        source_block = await self.block_repository.get_by_id(source_block_id)
        if not source_block:
              logging_client.warning(f"Block with id {source_block_id} was not found")
              raise HTTPException(status_code=404, detail=f"Block with id {source_block_id} not found")

        target_block = await self.block_repository.get_by_id(target_block_id)
        if not target_block:
              logging_client.warning(f"Block with id {target_block_id} was not found")
              raise HTTPException(status_code=404, detail=f"Block with id {target_block_id} not found")

        bot = await self.bot_repository.get_by_id(source_block.bot_id)
        if not bot:
             logging_client.warning(f"Bot with id {source_block.bot_id} was not found")
             raise BotNotFoundException(bot_id=source_block.bot_id)

        await self.logic_manager.connect_blocks(source_block_id, target_block_id)
        await self.block_repository.create_connection(source_block_id=source_block_id, target_block_id=target_block_id, bot_id=source_block.bot_id)


        logging_client.info(f"Connection created successfully for block id: {source_block_id} and block id: {target_block_id}")
        return SuccessResponse(message="Connection created successfully")