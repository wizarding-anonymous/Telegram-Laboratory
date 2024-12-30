from typing import List, Dict, Any, Optional
from src.core.logic_manager.handlers.utils import get_template
from src.core.utils import handle_exceptions
from src.integrations.telegram.client import TelegramClient
from src.config import settings
from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class MediaGroupHandler:
    """
    Handler for processing media group blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client
        
    @handle_exceptions
    async def handle_media_group(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any], bot_logic: Dict[str, Any], user_message: str) -> Optional[int]:
        """
        Handles sending a media group to a telegram chat.

        Args:
            block (dict): The media group block details from database.
            chat_id (int): Telegram chat ID where to send the media group.
            variables (dict): Dictionary of variables
            bot_logic (dict) : bot logic
        Returns:
             Optional[int]: next_block_id if it exists, otherwise None
        """
        logging_client.info(f"Handling media group block {block.get('id')} for chat_id: {chat_id}")
        content = block.get("content", {})
        media_items = content.get("items", [])
        
        if not media_items:
            logging_client.warning(f"Media items is not defined in media group block with id: {block.get('id')}")
            return None

        processed_media_items = []
        for item in media_items:
          template_caption = item.get('caption')
          if template_caption:
              template = get_template(template_caption)
              rendered_caption = template.render(variables=variables)
              item['caption'] = rendered_caption
          processed_media_items.append(item)

        
        sent_messages = await self.telegram_client.send_media_group(chat_id=chat_id, media=processed_media_items)
        logging_client.info(f"Media group was send successfully to chat_id: {chat_id}")
        from src.core.logic_manager import LogicManager
        logic_manager = LogicManager()
        next_blocks = await logic_manager._get_next_blocks(block.get("id"), bot_logic)
        if next_blocks:
          return next_blocks[0].get("id")
        return None