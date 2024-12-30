from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException

from src.api.schemas import (
    SuccessResponse,
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate
)
from src.core.utils import handle_exceptions, validate_block_ids, validate_connection_data
from src.db.repositories import BlockRepository
from src.integrations import get_current_user
from src.integrations.logging_client import LoggingClient
from src.core.utils.exceptions import BotNotFoundException
from src.core.logic_manager.base import LogicManager
from src.config import settings
from src.db.models import Connection

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


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
        bot_id: int,
        connection: ConnectionCreate,
        user: dict = Depends(get_current_user),
    ) -> ConnectionResponse:
        """Creates a connection between two blocks."""
        logging_client.info(
            f"Creating connection from block id: {connection.source_block_id} to block id: {connection.target_block_id}"
        )
        
        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user.get('id')} does not have permission to create block connections")
             raise HTTPException(status_code=403, detail="Permission denied")
        
        validate_connection_data(connection.model_dump())
        validate_block_ids([connection.source_block_id, connection.target_block_id])
        
        source_block = await self.block_repository.get_by_id(connection.source_block_id)
        if not source_block:
            logging_client.warning(f"Block with id {connection.source_block_id} was not found")
            raise HTTPException(status_code=404, detail=f"Block with id {connection.source_block_id} not found")
        
        target_block = await self.block_repository.get_by_id(connection.target_block_id)
        if not target_block:
            logging_client.warning(f"Block with id {connection.target_block_id} was not found")
            raise HTTPException(status_code=404, detail=f"Block with id {connection.target_block_id} not found")


        bot = await self.block_repository.get_bot_by_block_id(connection.source_block_id)
        if not bot:
             logging_client.warning(f"Bot with id {bot_id} was not found")
             raise BotNotFoundException(bot_id=bot_id)
        
        if source_block.bot_id != bot_id or target_block.bot_id != bot_id:
             logging_client.warning(f"Source or target blocks does not belong to bot {bot_id}")
             raise HTTPException(status_code=400, detail=f"Source or target blocks does not belong to bot {bot_id}")
        

        await self.logic_manager.connect_blocks(source_block.id, target_block.id)
        new_connection = await self.block_repository.create_connection(
            source_block_id=source_block.id,
            target_block_id=target_block.id,
            type=connection.type,
            bot_id=bot_id
            )
        logging_client.info(f"Connection created successfully for block id: {source_block.id} and block id: {target_block.id}")
        return ConnectionResponse(**new_connection.model_dump())


    @handle_exceptions
    async def get_connection(
            self,
            connection_id: int,
            user: dict = Depends(get_current_user),
    ) -> ConnectionResponse:
        """Gets connection between two blocks."""
        logging_client.info(
            f"Getting connection with id: {connection_id}"
        )
        
        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user.get('id')} does not have permission to create block connections")
             raise HTTPException(status_code=403, detail="Permission denied")
        
        connection = await self.block_repository.get_connection_by_id(connection_id)
        if not connection:
            logging_client.warning(f"Connection with id {connection_id} was not found")
            raise HTTPException(status_code=404, detail=f"Connection with id {connection_id} not found")
        
        logging_client.info(f"Connection with id: {connection_id} retrieved successfully")
        return ConnectionResponse(**connection.model_dump())
    
    
    @handle_exceptions
    async def update_connection(
        self,
        connection_id: int,
        connection_data: ConnectionUpdate,
        user: dict = Depends(get_current_user),
    ) -> ConnectionResponse:
        """Updates a connection between two blocks."""
        logging_client.info(
            f"Updating connection with id: {connection_id}"
        )
        
        if "admin" not in user.get("roles", []):
             logging_client.warning(f"User with id: {user.get('id')} does not have permission to update block connections")
             raise HTTPException(status_code=403, detail="Permission denied")
        
        connection = await self.block_repository.get_connection_by_id(connection_id)
        if not connection:
            logging_client.warning(f"Connection with id {connection_id} was not found")
            raise HTTPException(status_code=404, detail=f"Connection with id {connection_id} not found")
        
        if connection_data.source_block_id:
             source_block = await self.block_repository.get_by_id(connection_data.source_block_id)
             if not source_block:
                logging_client.warning(f"Block with id {connection_data.source_block_id} was not found")
                raise HTTPException(status_code=404, detail=f"Block with id {connection_data.source_block_id} not found")
        
        if connection_data.target_block_id:
            target_block = await self.block_repository.get_by_id(connection_data.target_block_id)
            if not target_block:
                logging_client.warning(f"Block with id {connection_data.target_block_id} was not found")
                raise HTTPException(status_code=404, detail=f"Block with id {connection_data.target_block_id} not found")

        
        if connection_data.source_block_id and connection_data.target_block_id:
            validate_block_ids([connection_data.source_block_id, connection_data.target_block_id])
        
        bot_id = await self.block_repository.get_bot_id_by_connection_id(connection_id=connection_id)
        if not bot_id:
            logging_client.warning(f"Bot for connection id {connection_id} was not found")
            raise BotNotFoundException(bot_id=bot_id)

        if  connection_data.source_block_id and source_block.bot_id != bot_id or connection_data.target_block_id and target_block.bot_id != bot_id:
             logging_client.warning(f"Source or target blocks does not belong to bot {bot_id}")
             raise HTTPException(status_code=400, detail=f"Source or target blocks does not belong to bot {bot_id}")
        

        updated_connection = await self.block_repository.update_connection(connection_id=connection_id, connection_data=connection_data.model_dump(exclude_unset=True))
        logging_client.info(f"Connection with id: {connection_id} updated successfully")
        return ConnectionResponse(**updated_connection.model_dump())


    @handle_exceptions
    async def delete_connection(
        self, connection_id: int, user: dict = Depends(get_current_user)
    ) -> SuccessResponse:
        """Deletes a connection between two blocks."""
        logging_client.info(
            f"Deleting connection with id: {connection_id}"
        )
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user.get('id')} does not have permission to delete block connections")
            raise HTTPException(status_code=403, detail="Permission denied")

        connection = await self.block_repository.get_connection_by_id(connection_id)
        if not connection:
             logging_client.warning(f"Connection with id {connection_id} was not found")
             raise HTTPException(status_code=404, detail=f"Connection with id {connection_id} not found")
        
        bot_id = await self.block_repository.get_bot_id_by_connection_id(connection_id=connection_id)
        if not bot_id:
             logging_client.warning(f"Bot for connection id {connection_id} was not found")
             raise BotNotFoundException(bot_id=bot_id)


        await self.block_repository.delete_connection(connection_id)
        logging_client.info(f"Connection with id: {connection_id} deleted successfully")
        return SuccessResponse(message="Connection deleted successfully")