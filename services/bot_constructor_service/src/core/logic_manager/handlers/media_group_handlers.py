from typing import List, Dict, Any
from src.core.logic_manager.handlers.utils import get_template
from src.core.utils import handle_exceptions
from src.integrations.telegram.client import TelegramClient


class MediaGroupHandler:
    """
    Handler for processing media group blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client
        
    @handle_exceptions
    async def handle_media_group(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> List[Dict[str, Any]]:
        """
        Handles sending a media group to a telegram chat.

        Args:
            block (dict): The media group block details from database.
            chat_id (int): Telegram chat ID where to send the media group.
            variables (dict): Dictionary of variables
        
        Returns:
             List[Dict[str, Any]]: List of response objects
        """

        media_items = block.get("content", {}).get("items", [])
        
        if not media_items:
             return []


        processed_media_items = []
        for item in media_items:
          template_caption = item.get('caption')
          if template_caption:
              template = get_template(template_caption)
              rendered_caption = template.render(variables=variables)
              item['caption'] = rendered_caption
          processed_media_items.append(item)

        
        sent_messages = await self.telegram_client.send_media_group(chat_id=chat_id, media=processed_media_items)
        
        return sent_messages