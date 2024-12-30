from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Flow, Connection
from src.core.utils import handle_exceptions
from src.config import settings
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class FlowRepository:
    """
    Repository for performing database operations on flow chart blocks.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_exceptions
    async def create(self, bot_id: int, logic: dict) -> Flow:
        """
        Creates a new flow chart block.

        Args:
            bot_id (int): The ID of the bot to associate the block with.
            logic (dict): The logic definition of the flow chart block.

        Returns:
            Flow: The created flow chart block object.
        """
        logging_client.info(f"Creating flow chart block for bot_id: {bot_id}")
        new_flow = Flow(bot_id=bot_id, logic=logic)
        self.session.add(new_flow)
        await self.session.commit()
        await self.session.refresh(new_flow)
        logging_client.info(f"Flow chart block with id {new_flow.id} created successfully for bot_id: {bot_id}")
        return new_flow

    @handle_exceptions
    async def get_by_id(self, block_id: int) -> Optional[Flow]:
        """
        Retrieves a flow chart block by its ID.

        Args:
            block_id (int): The ID of the flow chart block.

        Returns:
            Optional[Flow]: The flow chart block object, or None if not found.
        """
        logging_client.info(f"Getting flow chart block with id: {block_id}")
        flow = await self.session.get(Flow, block_id)
        if flow:
            logging_client.info(f"Flow chart block with id: {block_id} was found")
        else:
            logging_client.warning(f"Flow chart block with id: {block_id} was not found")
        return flow

    @handle_exceptions
    async def update(self, block_id: int, logic: dict) -> Optional[Flow]:
        """
        Updates an existing flow chart block.

        Args:
            block_id (int): The ID of the flow chart block to update.
            logic (dict): The new logic definition of the flow chart block.

        Returns:
            Optional[Flow]: The updated flow chart block object, or None if not found.
        """
        logging_client.info(f"Updating flow chart block with id: {block_id}")
        flow = await self.session.get(Flow, block_id)
        if not flow:
            logging_client.warning(f"Flow chart block with id: {block_id} was not found")
            return None

        flow.logic = logic
        flow.type = "flow_chart"
        await self.session.commit()
        await self.session.refresh(flow)
        logging_client.info(f"Flow chart block with id: {block_id} was updated successfully")
        return flow

    @handle_exceptions
    async def delete(self, block_id: int) -> None:
        """
        Deletes a flow chart block by its ID.

        Args:
            block_id (int): The ID of the flow chart block to delete.
        """
        logging_client.info(f"Deleting flow chart block with id: {block_id}")
        flow = await self.session.get(Flow, block_id)
        if flow:
            await self.session.delete(flow)
            await self.session.commit()
            logging_client.info(f"Flow chart block with id: {block_id} was deleted successfully")
        else:
           logging_client.warning(f"Flow chart block with id: {block_id} was not found")
    
    @handle_exceptions
    async def _get_next_blocks(self, block_id: int) -> List[Flow]:
        """
        Get next blocks from database.

        Args:
            block_id (int): The ID of the source block.
        Returns:
            List[Block]: list of next blocks
        """
        logging_client.info(f"Get next block for flow chart block with id: {block_id}")
        query = select(Connection.target_block_id).where(Connection.source_block_id == block_id)
        result = await self.session.execute(query)
        target_ids = [row[0] for row in result.all()]
        if target_ids:
             next_blocks = await self.session.execute(select(Flow).where(Flow.id.in_(target_ids)))
             return next_blocks.scalars().all()
        else:
            logging_client.info(f"Next blocks were not found for flow chart block with id: {block_id}")
            return []