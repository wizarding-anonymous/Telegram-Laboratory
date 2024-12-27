from typing import List, Optional

from fastapi import HTTPException, Depends, Query
from loguru import logger

from src.api.schemas import (
    BlockCreate,
    BlockUpdate,
    BlockResponse,
    BlockConnection,
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    ListResponse,
)
from src.core.utils import (
    handle_exceptions,
    validate_block_type,
    validate_bot_id,
    validate_block_ids,
    validate_connections,
    validate_content,
)
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name="bot_constructor")

class BlockController:
    """
    Controller for managing blocks.
    """

    def __init__(
        self,
        block_repository: BlockRepository = Depends(),
    ):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_block(
        self, block_create: BlockCreate, user: dict = Depends(get_current_user)
    ) -> BlockResponse:
        """Creates a new block."""
        logging_client.info(f"Creating block of type: {block_create.type}")

        validate_block_type(block_create.type)
        validate_bot_id(block_create.bot_id)
        validate_content(block_create.content)
        
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User with id: {user['id']} does not have permission to create blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        block = await self.block_repository.create(block_create.model_dump())
        logging_client.info(f"Block with id: {block.id} created successfully")
        return BlockResponse(**block.model_dump())

    @handle_exceptions
    async def get_block(
        self, block_id: int, user: dict = Depends(get_current_user)
    ) -> BlockResponse:
        """Gets a specific block by id."""
        logging_client.info(f"Getting block with id: {block_id}")
        validate_block_ids([block_id])
        block = await self.block_repository.get_by_id(block_id)
        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise HTTPException(status_code=404, detail="Block not found")

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to get blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
            
        logging_client.info(f"Block with id: {block_id} retrieved successfully")
        return BlockResponse(**block.model_dump())

    @handle_exceptions
    async def list_blocks(
        self,
        bot_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        user: dict = Depends(get_current_user)
    ) -> PaginatedResponse[BlockResponse]:
        """Gets a list of blocks for the bot."""
        logging_client.info(f"Listing blocks for bot id: {bot_id}")
        validate_bot_id(bot_id)
        blocks, total = await self.block_repository.list_paginated(
            page=page, page_size=page_size, bot_id=bot_id
        )

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to list blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        block_list = [BlockResponse(**block.model_dump()) for block in blocks]
        logging_client.info(f"Found {len(block_list)} blocks for bot id: {bot_id}")
        return PaginatedResponse(
            items=block_list, page=page, page_size=page_size, total=total
        )

    @handle_exceptions
    async def update_block(
        self, block_id: int, block_update: BlockUpdate, user: dict = Depends(get_current_user)
    ) -> BlockResponse:
        """Updates an existing block."""
        logging_client.info(f"Updating block with id: {block_id}")
        validate_block_ids([block_id])
        
        block = await self.block_repository.get_by_id(block_id)

        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise HTTPException(status_code=404, detail="Block not found")
        
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to update blocks")
            raise HTTPException(status_code=403, detail="Permission denied")
            
        block_data = block_update.model_dump(exclude_unset=True)

        if block_data.get("type"):
            validate_block_type(block_data.get("type"))
        if block_data.get("content"):
            validate_content(block_data.get("content"))

        updated_block = await self.block_repository.update(block_id, block_data)
        logging_client.info(f"Block with id: {block_id} updated successfully")
        return BlockResponse(**updated_block.model_dump())

    @handle_exceptions
    async def delete_block(
        self, block_id: int, user: dict = Depends(get_current_user)
    ) -> SuccessResponse:
        """Deletes a block."""
        logging_client.info(f"Deleting block with id: {block_id}")
        validate_block_ids([block_id])
        
        block = await self.block_repository.get_by_id(block_id)

        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise HTTPException(status_code=404, detail="Block not found")
            
        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to delete blocks")
            raise HTTPException(status_code=403, detail="Permission denied")

        await self.block_repository.delete(block_id)
        logging_client.info(f"Block with id: {block_id} deleted successfully")
        return SuccessResponse(message="Block deleted successfully")

    @handle_exceptions
    async def create_connection(self, connection: BlockConnection, user: dict = Depends(get_current_user)) -> SuccessResponse:
        """Creates connection between blocks"""
        logging_client.info(f"Creating connection between block {connection.source_block_id} and block {connection.target_block_id}")
        validate_block_ids([connection.source_block_id, connection.target_block_id])

        if "admin" not in user.get("roles", []):
            logging_client.warning(f"User: {user['id']} does not have permission to create block connections")
            raise HTTPException(status_code=403, detail="Permission denied")
        
        source_block = await self.block_repository.get_by_id(connection.source_block_id)
        target_block = await self.block_repository.get_by_id(connection.target_block_id)

        if not source_block or not target_block:
            logging_client.warning(f"One or more blocks for connection were not found")
            raise HTTPException(status_code=404, detail="One or more blocks for connection were not found")
        
        validate_connections(connection.source_block_id, connection.target_block_id)
        await self.block_repository.create_connection(connection.source_block_id, connection.target_block_id)
        logging_client.info(f"Connection created between block {connection.source_block_id} and block {connection.target_block_id}")
        return SuccessResponse(message="Connection created successfully")