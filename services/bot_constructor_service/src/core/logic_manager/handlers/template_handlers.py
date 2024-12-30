from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.db.repositories import BlockRepository, BotRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.core.utils import validate_bot_id
from src.core.logic_manager.handlers.utils import get_template
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")

class TemplateHandler:
    """
    Handler for processing template-related blocks.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.block_repository = BlockRepository(session)
        self.bot_repository = BotRepository(session)

    @handle_exceptions
    async def handle_create_from_template(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any], bot_id: int
    ) -> None:
        """
        Creates blocks for a bot based on a template.

        Args:
            block (dict): The create from template block details from the database.
            bot_id (int): Bot id that will be populated from template
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        validate_bot_id(bot_id)
        content = block.get("content", {})
        template_bot_id = content.get("template_bot_id")

        if not template_bot_id:
            logging_client.warning("Template bot id was not provided")
            return

        template_bot = await self.bot_repository.get(template_bot_id)
        if not template_bot:
             logging_client.warning(f"Template bot with id {template_bot_id} not found")
             return

        blocks = await self.block_repository.get_by_bot_id(template_bot_id)
        if not blocks:
            logging_client.warning(
                f"Template bot with id {template_bot_id} does not contain any blocks"
            )
            return
        from src.core.logic_manager import LogicManager

        logic_manager = LogicManager()
        for template_block in blocks:
            new_block_content = template_block.content.copy()
            if isinstance(new_block_content, dict):
              if new_block_content.get("content"):
                  if isinstance(new_block_content.get("content"),dict):
                       new_block_content["content"] = {k: get_template(str(v)).render(variables=variables) if isinstance(v, str) else v for k, v in new_block_content["content"].items() if k != 'id'}
                  elif isinstance(new_block_content.get("content"), str):
                      new_block_content["content"] = get_template(new_block_content.get("content")).render(variables=variables)
              new_block_content = {k: get_template(str(v)).render(variables=variables) if isinstance(v, str) else v for k, v in new_block_content.items() if k != 'id' }

            
            await self.block_repository.create(
                bot_id=bot_id,
                type=template_block.type,
                content=new_block_content,
            )

            next_blocks = await logic_manager._get_next_blocks(template_block.id, template_bot.logic)
            if next_blocks:
                for next_block in next_blocks:
                    new_block_content = next_block.content.copy()
                    if isinstance(new_block_content, dict):
                      if new_block_content.get("content"):
                          if isinstance(new_block_content.get("content"),dict):
                            new_block_content["content"] = {k: get_template(str(v)).render(variables=variables) if isinstance(v, str) else v for k, v in new_block_content["content"].items() if k != 'id'}
                          elif isinstance(new_block_content.get("content"), str):
                              new_block_content["content"] = get_template(new_block_content.get("content")).render(variables=variables)
                      new_block_content = {k: get_template(str(v)).render(variables=variables) if isinstance(v, str) else v for k, v in new_block_content.items() if k != 'id'}
                    await self.block_repository.create(
                        bot_id=bot_id,
                        type = next_block.type,
                        content=new_block_content
                    )
            logging_client.info(
                f"Created blocks from template {template_bot_id} for bot {bot_id}"
            )