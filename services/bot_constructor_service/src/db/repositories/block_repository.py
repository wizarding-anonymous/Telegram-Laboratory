from typing import List, Dict, Any, Tuple, Optional
from fastapi import HTTPException, Depends
from sqlalchemy import select, update, delete, insert, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.models import Block, Connection
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.core.utils.exceptions import BlockNotFoundException

logging_client = LoggingClient(service_name="bot_constructor")


class BlockRepository:
    """
    Repository for managing block data in the database.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        logging_client.info("BlockRepository initialized")

    @handle_exceptions
    async def create(self, block_data: Dict[str, Any], type: str = None) -> Block:
        """Creates a new block."""
        logging_client.info(f"Creating block with data: {block_data}")
        if type:
            block = Block(**block_data, type=type)
        else:
            block = Block(**block_data)
        self.session.add(block)
        await self.session.commit()
        await self.session.refresh(block)
        logging_client.info(f"Block with id: {block.id} created successfully")
        return block

    @handle_exceptions
    async def get_by_id(self, block_id: int) -> Optional[Block]:
        """Gets a block by its ID."""
        logging_client.info(f"Getting block with id: {block_id}")
        result = await self.session.execute(select(Block).where(Block.id == block_id))
        block = result.scalar_one_or_none()
        if not block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise BlockNotFoundException(block_id=block_id)
        logging_client.info(f"Block with id: {block_id} retrieved successfully")
        return block
    
    @handle_exceptions
    async def list_by_ids(self, block_ids: List[int]) -> List[Block]:
        """Gets a list of blocks by their IDs."""
        logging_client.info(f"Getting list of blocks by ids: {block_ids}")
        result = await self.session.execute(select(Block).where(Block.id.in_(block_ids)))
        blocks = list(result.scalars().all())
        logging_client.info(f"Found {len(blocks)} blocks")
        return blocks


    @handle_exceptions
    async def get_all_by_bot(
        self, bot_id: int, skip: int = 0, limit: int = 100
    ) -> List[Block]:
        """Gets a list of blocks for a specific bot."""
        logging_client.info(f"Getting list of blocks for bot id: {bot_id}")
        result = await self.session.execute(
            select(Block)
            .where(Block.bot_id == bot_id)
            .offset(skip)
            .limit(limit)
        )
        blocks = list(result.scalars().all())
        logging_client.info(f"Found {len(blocks)} blocks for bot id: {bot_id}")
        return blocks

    @handle_exceptions
    async def list_paginated(self, page: int, page_size: int, bot_id: int, type: str = None) -> Tuple[List[Block], int]:
        """Gets a paginated list of blocks for a specific bot."""
        logging_client.info(f"Getting paginated list of blocks for bot_id: {bot_id}")
        offset = (page - 1) * page_size
        query = select(Block).where(Block.bot_id == bot_id)
        if type:
            query = query.where(Block.type == type)
        
        count_query = await self.session.execute(select(func.count()).select_from(query))
        total = count_query.scalar_one()
        
        query = query.order_by(Block.created_at.desc()).offset(offset).limit(page_size)
        
        result = await self.session.execute(query)
        blocks = list(result.scalars().all())
        logging_client.info(f"Found {len(blocks)} of {total} blocks for bot id: {bot_id}")
        return blocks, total


    @handle_exceptions
    async def update(self, block_id: int, block_data: Dict[str, Any]) -> Block:
        """Updates an existing block."""
        logging_client.info(f"Updating block with id: {block_id}")
        query = update(Block).where(Block.id == block_id).values(block_data).returning(Block)
        result = await self.session.execute(query)
        updated_block = result.scalar_one_or_none()
        if not updated_block:
            logging_client.warning(f"Block with id: {block_id} not found")
            raise BlockNotFoundException(block_id=block_id)
        await self.session.commit()
        logging_client.info(f"Block with id: {block_id} updated successfully")
        return updated_block

    @handle_exceptions
    async def delete(self, block_id: int) -> bool:
        """Deletes a block."""
        logging_client.info(f"Deleting block with id: {block_id}")
        query = delete(Block).where(Block.id == block_id)
        result = await self.session.execute(query)
        await self.session.commit()
        if result.rowcount > 0 :
             logging_client.info(f"Block with id: {block_id} deleted successfully")
             return True
        else:
             logging_client.warning(f"Block with id: {block_id} not found or already deleted")
             return False
    
    @handle_exceptions
    async def create_connection(self, source_block_id: int, target_block_id: int) -> None:
        """Creates connection between two blocks."""
        logging_client.info(f"Creating connection between block {source_block_id} and block {target_block_id}")
        
        connection = Connection(source_block_id=source_block_id, target_block_id=target_block_id)
        self.session.add(connection)
        await self.session.commit()
        
        logging_client.info(f"Connection created between block {source_block_id} and block {target_block_id}")

    @handle_exceptions
    async def get_connected_blocks(self, block_id: int) -> List[Block]:
        """Retrieves connected blocks for specific block."""
        logging_client.info(f"Getting connected blocks for block id: {block_id}")
        
        query = (
            select(Block)
            .join(Connection, Connection.target_block_id == Block.id)
            .where(Connection.source_block_id == block_id)
        )
        result = await self.session.execute(query)
        blocks = list(result.scalars().all())
        logging_client.info(f"Found {len(blocks)} connected blocks for block id: {block_id}")
        return blocks
    
    @handle_exceptions
    async def add_connection(self, source_block_id: int, target_block_id: int) -> None:
        """Adds connection between blocks"""
        logging_client.info(f"Adding connection from block {source_block_id} to block {target_block_id}")
        connection = Connection(source_block_id=source_block_id, target_block_id=target_block_id)
        self.session.add(connection)
        await self.session.commit()
        logging_client.info(f"Connection from block {source_block_id} to block {target_block_id} added successfully")