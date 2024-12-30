import asyncio
import json
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

import httpx
from fastapi import HTTPException, Depends
from jinja2 import BaseLoader, Environment
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.core.utils.exceptions import BlockNotFoundException
from src.core.utils.validators import (
    validate_block_type,
    validate_api_request_data,
    validate_database_data,
    validate_variable_data,
    validate_timer_data,
    validate_state_machine_data,
    validate_custom_filter_data,
    validate_rate_limiting_data,
    validate_content,
)
from src.db.database import get_session
from src.db.repositories import BlockRepository, BotRepository
from src.integrations.auth_service import AuthService, get_current_user
from src.integrations.logging_client import LoggingClient
from src.integrations.redis_client import redis_client
from src.integrations.telegram import TelegramClient
from dataclasses import dataclass, field


@dataclass
class Block:
    id: int
    type: str
    content: Optional[Dict[str, Any]] = field(default_factory=dict)
    connections: Optional[List[int]] = field(default_factory=list)


class LogicManager:
    """
    Manages the execution of bot logic based on blocks and connections.
    """

    def __init__(
        self,
        block_repository: BlockRepository = Depends(),
        bot_repository: BotRepository = Depends(),
        telegram_client: TelegramClient = Depends(),
        auth_service: AuthService = Depends(),
    ):
        self.block_repository = block_repository
        self.bot_repository = bot_repository
        self.telegram_client = telegram_client
        self.auth_service = auth_service
        self.template_env = Environment(loader=BaseLoader())
        self.logging_client = LoggingClient(service_name="bot_constructor")
        self.http_client = httpx.AsyncClient()
        from src.core.logic_manager.handlers import (
              message_handlers,
              keyboard_handlers,
              flow_handlers,
              api_handlers,
              control_handlers,
          )
        self.handlers: Dict[str, Callable[..., Any]] = {
            "text_message": message_handlers.handle_text_message_block,
            "send_text": message_handlers.handle_send_text_block,
            "keyboard": keyboard_handlers.handle_keyboard_block,
            "if_condition": flow_handlers.handle_if_condition_block,
            "loop": flow_handlers.handle_loop_block,
            "api_request": api_handlers.handle_api_request_block,
            "database": api_handlers.handle_database_block,
            "webhook": api_handlers.handle_webhook_block,
            "callback": keyboard_handlers.handle_callback_block,
            "variable": control_handlers.handle_variable_block,
            "photo_message": message_handlers.handle_media_message_block,
            "video_message": message_handlers.handle_media_message_block,
            "audio_message": message_handlers.handle_media_message_block,
            "document_message": message_handlers.handle_media_message_block,
            "location_message": message_handlers.handle_location_message_block,
            "sticker_message": message_handlers.handle_media_message_block,
            "contact_message": message_handlers.handle_contact_message_block,
            "venue_message": message_handlers.handle_venue_message_block,
            "game_message": message_handlers.handle_game_message_block,
            "poll_message": message_handlers.handle_poll_message_block,
            "send_photo": message_handlers.handle_send_media_block,
            "send_video": message_handlers.handle_send_media_block,
            "send_audio": message_handlers.handle_send_media_block,
            "send_document": message_handlers.handle_send_media_block,
            "send_location": message_handlers.handle_send_location_block,
            "send_sticker": message_handlers.handle_send_media_block,
            "send_contact": message_handlers.handle_send_contact_block,
            "send_venue": message_handlers.handle_send_venue_block,
            "send_game": message_handlers.handle_send_game_block,
            "send_poll": message_handlers.handle_send_poll_block,
            "try_catch": control_handlers.handle_try_catch_block,
            "raise_error": control_handlers.handle_raise_error_block,
            "handle_exception": control_handlers.handle_handle_exception_block,
            "log_message": control_handlers.handle_log_message_block,
            "timer": control_handlers.handle_timer_block,
            "state_machine": flow_handlers.handle_state_machine_block,
            "custom_filter": flow_handlers.handle_custom_filter_block,
            "rate_limiting": control_handlers.handle_rate_limiting_block,
        }

    async def close(self):
        await self.http_client.aclose()

    @handle_exceptions
    async def execute_bot_logic(
        self, bot_id: int, chat_id: int, user_message: str, user: dict = Depends(get_current_user)
    ) -> None:
        """Executes bot logic based on provided bot_id and chat_id."""
        self.logging_client.info(
            f"Executing bot logic for bot_id: {bot_id}, chat_id: {chat_id}"
        )

        # Get the bot and its logic
        bot = await self.bot_repository.get_by_id(bot_id)
        if not bot or not bot.logic:
            self.logging_client.warning(
                f"Bot or bot logic was not found for bot_id: {bot_id}"
            )
            raise HTTPException(
                status_code=404, detail="Bot or bot logic was not found"
            )
        
        if "admin" not in user.get("roles", []):
           self.logging_client.warning(f"User: {user['id']} does not have permission to execute bot logic")
           raise HTTPException(status_code=403, detail="Permission denied")
        

        bot_logic = bot.logic

        # Get the initial block ID from bot logic
        start_block_id = bot_logic.get("start_block_id")
        if not start_block_id:
            self.logging_client.warning(
                f"Start block id not found for bot_id: {bot_id}"
            )
            raise HTTPException(
                status_code=404, detail="Start block id not found for bot"
            )

        start_block = await self.block_repository.get_by_id(start_block_id)
        if not start_block:
            self.logging_client.warning(
                f"Start block with id: {start_block_id} not found for bot_id: {bot_id}"
            )
            raise BlockNotFoundException(block_id=start_block_id)

        await self._process_block(
            Block(**start_block.model_dump()), chat_id, user_message, bot_logic,
             variables={}
        )

        self.logging_client.info(
            f"Bot logic for bot_id: {bot_id}, chat_id: {chat_id} executed successfully"
        )

    async def _process_block(
        self,
        block: Block,
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Processes a single block of bot logic."""
        if variables is None:
            variables = {}
        self.logging_client.info(
            f"Processing block with id: {block.id}, type: {block.type}"
        )
        validate_block_type(block.type)
        # Extract data from content dict
        content = block.content if block.content else {}
        validate_content(content)
        handler = self.handlers.get(block.type)
        if handler:
            await self._safe_execute(
                handler,
                content,
                chat_id,
                user_message,
                bot_logic,
                variables,
                block,
            )
        else:
            self.logging_client.warning(f"Unsupported block type: {block.type}")
            return

        # Get next blocks based on current block's connections and process them
        next_blocks = await self._get_next_blocks(block.id, bot_logic)
        if next_blocks:
            await asyncio.gather(
                *[
                    self._process_block(
                        Block(**next_block.model_dump()),
                        chat_id,
                        user_message,
                        bot_logic,
                        variables,
                    )
                    for next_block in next_blocks
                ]
            )
        self.logging_client.info(
            f"Finished processing block with id: {block.id}, type: {block.type}"
        )

    async def _safe_execute(
        self,
        handler: Callable[..., Any],
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ):
        """Safely executes a handler with exception handling."""
        try:
            await handler(content, chat_id, user_message, bot_logic, variables, block)
        except HTTPException as he:
            self.logging_client.error(
                f"HTTPException in block {block.id}: {he.detail}"
            )
            raise
        except httpx.HTTPError as he:
            self.logging_client.error(
                f"HTTPError in block {block.id}: {he}"
            )
            raise
        except Exception as e:
            self.logging_client.error(
                f"Error during processing block: {block.id}, type: {block.type}. Error: {e}"
            )
            raise

    async def _get_next_blocks(
        self, block_id: int, bot_logic: Dict[str, Any]
    ) -> List[Block]:
        """Retrieves next blocks based on connections."""
        self.logging_client.info(f"Retrieving next blocks for block id: {block_id}")

        connections = bot_logic.get("connections", [])
        next_block_ids = [
            connection
            for connection in connections
            if connection == block_id
        ]

        connected_blocks = []
        if next_block_ids:
            blocks = await self.block_repository.list_by_ids(next_block_ids)
            connected_blocks = [Block(**block.model_dump()) for block in blocks]

        return connected_blocks

    @lru_cache(maxsize=128)
    def get_template(self, template_str: str):
        """Returns a cached Jinja2 template."""
        return self.template_env.from_string(template_str)

    async def initialize_block(self, block: Any) -> None:
       """Initialize block in logic manager"""
       self.logging_client.info(f"Initializing block {block.id} of type {block.type}")

    async def update_block(self, block: Any) -> None:
        """Updates block in logic manager"""
        self.logging_client.info(f"Updating block {block.id} of type {block.type}")

    async def remove_block(self, block_id: int) -> None:
        """Removes block from logic manager"""
        self.logging_client.info(f"Removing block {block_id}")

    async def connect_blocks(self, source_block_id: int, target_block_id: int) -> None:
       """Connect blocks in logic manager"""
       self.logging_client.info(
           f"Connecting blocks {source_block_id} and {target_block_id} in logic manager"
       )