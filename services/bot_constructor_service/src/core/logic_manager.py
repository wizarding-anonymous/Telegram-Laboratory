from typing import Dict, Any, List
from fastapi import HTTPException
from loguru import logger

from src.core.utils import handle_exceptions
from src.db.repositories import BlockRepository
from src.integrations.telegram.telegram_api import TelegramAPI
from src.integrations.logging_client import LoggingClient
from src.integrations.auth_service import AuthService

logging_client = LoggingClient(service_name="bot_constructor")


class LogicManager:
    """
    Manages the execution of bot logic based on blocks and connections.
    """

    def __init__(
            self,
            block_repository: BlockRepository,
            telegram_api: TelegramAPI,
            auth_service: AuthService,
    ):
        self.block_repository = block_repository
        self.telegram_api = telegram_api
        self.auth_service = auth_service

    @handle_exceptions
    async def execute_bot_logic(self, bot_id: int, chat_id: int, user_message: str) -> None:
        """Executes bot logic based on provided bot_id and chat_id."""
        logging_client.info(f"Executing bot logic for bot_id: {bot_id}, chat_id: {chat_id}")
        
        # Get the initial block for the bot (e.g. start block)
        start_block = await self._get_start_block(bot_id)
        if not start_block:
            logging_client.warning(f"Start block not found for bot_id: {bot_id}")
            raise HTTPException(status_code=404, detail="Start block not found for bot")

        await self._process_block(start_block, chat_id, user_message)
        
        logging_client.info(f"Bot logic for bot_id: {bot_id}, chat_id: {chat_id} executed successfully")

    async def _get_start_block(self, bot_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves start block for the bot"""
        logging_client.info(f"Retrieving start block for bot_id: {bot_id}")
        #  Here you need to implement logic to find start block based on a condition (e.g. block type is "start")
        blocks = await self.block_repository.list_by_bot_id(bot_id)
        for block in blocks:
            if block.type == "start":
                return block
        logging_client.warning(f"No start block found for bot_id: {bot_id}")
        return None

    async def _process_block(self, block: Dict[str, Any], chat_id: int, user_message: str) -> None:
        """Processes a single block of bot logic."""
        logging_client.info(f"Processing block with id: {block.id}, type: {block.type}")
        
        # Extract data from content dict
        content = block.content if block.content else {}
        
        if block.type == "text_message":
            # Handle text message
            await self._handle_text_message(content, chat_id, user_message)
        elif block.type == "send_text":
             # Handle sending text
            await self._handle_send_text(content, chat_id)
        elif block.type == "keyboard":
            # Handle creation and send keyboard
            await self._handle_keyboard_block(content, chat_id)
        elif block.type == "if_condition":
           # Handle conditional block execution
           await self._handle_if_condition(block, chat_id, user_message)
        elif block.type == "loop":
            # Handle loop block execution
            await self._handle_loop_block(block, chat_id, user_message)
        elif block.type == "api_request":
            # Handle API request block execution
            await self._handle_api_request_block(content, chat_id)
        elif block.type == "database":
            # Handle Database block execution
            await self._handle_database_block(content, chat_id)
        else:
            logging_client.warning(f"Unsupported block type: {block.type}")
            # Handle unsupported block
            return
        
        # Get next blocks based on current block's connections and process them
        next_blocks = await self._get_next_blocks(block.id)
        if next_blocks:
            for next_block in next_blocks:
                await self._process_block(next_block, chat_id, user_message)
        logging_client.info(f"Finished processing block with id: {block.id}, type: {block.type}")

    async def _get_next_blocks(self, block_id: int) -> List[Dict[str, Any]]:
        """Retrieves next blocks based on connections."""
        logging_client.info(f"Retrieving next blocks for block id: {block_id}")
        connected_blocks = await self.block_repository.get_connected_blocks(block_id)
        return connected_blocks

    async def _handle_text_message(self, content: Dict[str, Any], chat_id: int, user_message: str) -> None:
        """Handles a text message block."""
        logging_client.info(f"Handling text message for chat_id: {chat_id}")
        if content and content.get("text"):
            logging_client.info(f"User sent: {user_message}. Block text: {content['text']}")
            if content["text"] in user_message:
                logging_client.info(f"User message matches with content")
                # Do nothing, message is already handled
                return
            else:
               logging_client.info(f"User message does not match with content")

    async def _handle_send_text(self, content: Dict[str, Any], chat_id: int) -> None:
        """Handles sending a text message block."""
        logging_client.info(f"Handling send text block for chat_id: {chat_id}")
        if content and content.get("text"):
             logging_client.info(f"Sending text message: {content['text']} to chat_id: {chat_id}")
             await self.telegram_api.send_message(chat_id, content["text"])

    async def _handle_keyboard_block(self, content: Dict[str, Any], chat_id: int) -> None:
        """Handles keyboard block."""
        logging_client.info(f"Handling keyboard block for chat_id: {chat_id}")
        if content and content.get("keyboard_type") and content.get("buttons"):
            keyboard_type = content.get("keyboard_type")
            buttons = content.get("buttons")

            if keyboard_type == "reply":
                await self.telegram_api.send_message(chat_id, "Please select option:", reply_markup=buttons)
            elif keyboard_type == "inline":
                await self.telegram_api.send_message(chat_id, "Please select option:", inline_keyboard=buttons)
            else:
                logging_client.warning(f"Unsupported keyboard type: {keyboard_type}")

    async def _handle_if_condition(self, block: Dict[str, Any], chat_id: int, user_message: str) -> None:
        """Handles if condition block."""
        logging_client.info(f"Handling if condition block: {block.id} for chat_id: {chat_id}")
        if block.content and block.content.get("condition"):
            condition = block.content["condition"]
            if condition in user_message:
                logging_client.info(f"Condition: {condition} is true for user message: {user_message}. Executing connected blocks.")
                 # Proceed to next blocks, assuming condition is met
                next_blocks = await self._get_next_blocks(block.id)
                if next_blocks:
                     for next_block in next_blocks:
                        await self._process_block(next_block, chat_id, user_message)
            else:
                logging_client.info(f"Condition: {condition} is false for user message: {user_message}. Skipping next blocks.")
                 # Do nothing, skip next blocks as the condition is not met.

    async def _handle_loop_block(self, block: Dict[str, Any], chat_id: int, user_message: str) -> None:
        """Handles loop block."""
        logging_client.info(f"Handling loop block: {block.id} for chat_id: {chat_id}")

        if block.content and block.content.get("loop_type"):
            loop_type = block.content["loop_type"]

            if loop_type == "for":
               count = block.content.get("count", 0)
               if count > 0:
                    for i in range(count):
                        logging_client.info(f"Executing loop iteration {i + 1} for block: {block.id}")
                        next_blocks = await self._get_next_blocks(block.id)
                        if next_blocks:
                             for next_block in next_blocks:
                                await self._process_block(next_block, chat_id, user_message)
               else:
                   logging_client.warning(f"Loop count is less or equals to 0")
                   return
            elif loop_type == "while":
                logging_client.warning(f"While loops are not implemented")
                # TODO: Add handling for while loop
                return
        else:
            logging_client.warning(f"Loop type was not defined in {block.id}")
            return

    async def _handle_api_request_block(self, content: Dict[str, Any], chat_id: int) -> None:
        """Handles API request block."""
        logging_client.info(f"Handling API request block for chat_id: {chat_id}")
        # TODO: Add handling logic for API requests
        if content and content.get("url") and content.get("method"):
            logging_client.info(f"Making API request to url: {content['url']}, method: {content['method']}")
            # Add handling of API requests
        else:
            logging_client.warning(f"API parameters not defined for api_request block")
            return

    async def _handle_database_block(self, content: Dict[str, Any], chat_id: int) -> None:
       """Handles database request block."""
       logging_client.info(f"Handling database request block for chat_id: {chat_id}")
        # TODO: Add handling for database requests
       if content and content.get("query"):
           logging_client.info(f"Executing database query: {content['query']}")
           # Add handling of Database requests
       else:
            logging_client.warning(f"Database query not defined for database block")
            return