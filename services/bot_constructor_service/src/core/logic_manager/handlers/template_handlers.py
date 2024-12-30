from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.db.repositories import BlockRepository, BotRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.core.utils import validate_bot_id


class TemplateHandler:
    """
    Handler for processing template-related blocks.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.block_repository = BlockRepository(session)
        self.bot_repository = BotRepository(session)

    @handle_exceptions
    async def handle_create_from_template(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any], bot_id: int) -> None:
        """
        Creates blocks for a bot based on a template.

        Args:
            block (dict): The create from template block details from database.
             bot_id (int): Bot id that will be populated from template
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        validate_bot_id(bot_id)

        template_bot_id = block.get("content", {}).get("template_bot_id")
        
        template_bot = await self.bot_repository.get(template_bot_id)
        if not template_bot:
          raise Exception(f"Template bot with id {template_bot_id} not found")

        blocks = await self.block_repository.get_by_bot_id(template_bot_id)
        if not blocks:
           raise Exception(f"Template bot with id {template_bot_id} does not contain any blocks")
        
        for template_block in blocks:
          new_block_content = template_block.content.copy()
          if new_block_content.get("content"):
            if isinstance(new_block_content.get("content"),dict):
              new_block_content["content"] = {k: v for k, v in new_block_content["content"].items() if k !='id'}
            
          await self.block_repository.create(
                  bot_id = bot_id,
                  type=template_block.type,
                  content=new_block_content
              )