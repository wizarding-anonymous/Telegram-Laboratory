from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from loguru import logger

from src.core.utils import handle_exceptions
from src.db.repositories import BlockRepository
from src.integrations.logging_client import LoggingClient
from src.config import settings


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class FlowChartManager:
    """
    Manages the flow chart representation of bot logic.
    """

    def __init__(
        self,
         block_repository: BlockRepository
    ):
        self.block_repository = block_repository

    @handle_exceptions
    async def get_flow_chart(self, bot_id: int) -> Dict[str, Any]:
        """Retrieves a flow chart representation of a bot's logic."""
        logging_client.info(f"Getting flow chart for bot_id: {bot_id}")
        
        bot = await self.block_repository.get_bot_by_id(bot_id)
        if not bot:
            logging_client.warning(f"Bot with id {bot_id} not found")
            return {}
        
        blocks = await self.block_repository.list_by_bot_id(bot_id)
        if not blocks:
            logging_client.warning(f"No blocks found for bot_id: {bot_id}")
            return {}

        flow_chart = self._build_flow_chart(blocks)
        logging_client.info(f"Flow chart for bot_id: {bot_id} built successfully")
        return flow_chart

    def _build_flow_chart(self, blocks: List[Any]) -> Dict[str, Any]:
        """Builds a flow chart representation from the provided blocks."""
        logging_client.info("Building flow chart from blocks")
        
        nodes = {}
        edges = []

        for block in blocks:
            block_id = block.id
            nodes[block_id] = {
                "id": block_id,
                "type": block.type,
                "content": block.content if block.content else {},
            }

            if hasattr(block, "connections") and block.connections:
                 for connection in block.connections:
                     edges.append({"source": block_id, "target": connection.target_block_id})
        
        logging_client.info(f"Flow chart built. Nodes: {len(nodes)}, Edges: {len(edges)}")
        return {"nodes": list(nodes.values()), "edges": edges}


    @handle_exceptions
    async def update_flow_chart(self, bot_id: int) -> Dict[str, Any]:
        """Updates the flow chart representation for a bot."""
        logging_client.info(f"Updating flow chart for bot_id: {bot_id}")
        bot = await self.block_repository.get_bot_by_id(bot_id)
        if not bot:
            logging_client.warning(f"Bot with id {bot_id} not found")
            return {}
        
        blocks = await self.block_repository.list_by_bot_id(bot_id)
        if not blocks:
             logging_client.warning(f"No blocks found for bot_id: {bot_id}")
             return {}
        
        updated_flow_chart = self._build_flow_chart(blocks)
        logging_client.info(f"Flow chart for bot_id: {bot_id} updated successfully")
        return updated_flow_chart