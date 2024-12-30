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
from src.integrations.telegram import TelegramClient, get_telegram_client
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
        auth_service: AuthService = Depends(),
        session: AsyncSession = Depends(get_session)

    ):
        self.block_repository = block_repository
        self.bot_repository = bot_repository
        self.auth_service = auth_service
        self.template_env = Environment(loader=BaseLoader())
        self.logging_client = LoggingClient(service_name="bot_constructor")
        self.http_client = httpx.AsyncClient()
        self.session = session
        from src.core.logic_manager.handlers import (
            message_handlers,
            keyboard_handlers,
            flow_handlers,
            api_handlers,
            control_handlers,
            chat_handlers,
            callback_handlers,
            template_handlers,
            user_handlers,
            error_handlers,
        )
        self.handlers: Dict[str, Callable[..., Any]] = {
            "text_message": message_handlers.TextMessageBlockHandler(self.telegram_client).handle_text_message,
            "send_text": message_handlers.TextMessageBlockHandler(self.telegram_client).handle_send_text,
            "keyboard": keyboard_handlers.KeyboardHandler(self.telegram_client).handle_keyboard,
            "if_condition": flow_handlers.FlowChartManager(self.telegram_client).handle_if_condition,
             "loop": flow_handlers.FlowChartManager(self.telegram_client).handle_loop,
             "api_request": api_handlers.ApiRequestHandler(self.telegram_client).handle_api_request,
            "database_connect": api_handlers.DatabaseHandler(self.telegram_client).handle_database_connect,
            "database_query": api_handlers.DatabaseHandler(self.telegram_client).handle_database_query,
            "set_webhook": api_handlers.WebhookHandler(self.telegram_client).handle_set_webhook,
            "delete_webhook": api_handlers.WebhookHandler(self.telegram_client).handle_delete_webhook,
            "handle_callback_query": callback_handlers.CallbackHandler(self.telegram_client).handle_callback_query,
            "send_callback_response": callback_handlers.CallbackHandler(self.telegram_client).handle_send_callback_response,
            "variable": control_handlers.ControlHandler().handle_variable_block,
            "photo_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_media_message,
            "video_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_media_message,
            "audio_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_media_message,
            "document_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_media_message,
            "location_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_location_message,
            "sticker_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_media_message,
            "contact_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_contact_message,
            "venue_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_venue_message,
            "game_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_game_message,
            "poll_message": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_poll_message,
            "send_photo": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_media,
            "send_video": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_media,
             "send_audio": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_media,
            "send_document": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_media,
            "send_location": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_location,
            "send_sticker": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_media,
            "send_contact": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_contact,
            "send_venue": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_venue,
            "send_game": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_game,
            "send_poll": message_handlers.MediaMessageBlockHandler(self.telegram_client).handle_send_poll,
            "try_catch": control_handlers.ControlHandler().handle_try_catch_block,
            "raise_error": control_handlers.ControlHandler().handle_raise_error_block,
            "handle_exception": control_handlers.ControlHandler().handle_handle_exception_block,
            "log_message": control_handlers.ControlHandler().handle_log_message_block,
            "timer": control_handlers.ControlHandler().handle_timer_block,
            "state_machine": flow_handlers.FlowChartManager(self.telegram_client).handle_state_machine,
            "custom_filter": flow_handlers.FlowChartManager(self.telegram_client).handle_custom_filter,
            "rate_limiting": control_handlers.ControlHandler().handle_rate_limiting_block,
            "get_chat_members": chat_handlers.ChatHandler(self.telegram_client).handle_get_chat_members,
            "ban_user": chat_handlers.ChatHandler(self.telegram_client).handle_ban_user,
            "unban_user": chat_handlers.ChatHandler(self.telegram_client).handle_unban_user,
            "set_chat_title": chat_handlers.ChatHandler(self.telegram_client).handle_set_chat_title,
            "set_chat_description": chat_handlers.ChatHandler(self.telegram_client).handle_set_chat_description,
             "pin_message": chat_handlers.ChatHandler(self.telegram_client).handle_pin_message,
             "unpin_message": chat_handlers.ChatHandler(self.telegram_client).handle_unpin_message,
             "create_from_template": template_handlers.TemplateHandler(self.session).handle_create_from_template,
             "save_user_data": user_handlers.UserHandler().handle_save_user_data,
             "retrieve_user_data": user_handlers.UserHandler().handle_retrieve_user_data,
             "clear_user_data": user_handlers.UserHandler().handle_clear_user_data,
             "manage_session": user_handlers.UserHandler().handle_manage_session,
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

        telegram_client = get_telegram_client(bot.library)
        self.telegram_client = telegram_client
        
        variables = {"bot_token": bot.token}

        await self._process_block(
            Block(**start_block.model_dump()), chat_id, user_message, bot_logic,
             variables=variables
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
    ) -> Optional[int]:
        """Processes a single block of bot logic."""
        if variables is None:
            variables = {}
        self.logging_client.info(
            f"Processing block with id: {block.id}, type: {block.type}"
        )
        validate_block_type(block.type)
        content = block.content if block.content else {}
        validate_content(content)
        handler = self.handlers.get(block.type)
        if handler:
           result = await self._safe_execute(
                handler,
                content,
                chat_id,
                user_message,
                bot_logic,
                variables,
                block,
            )
           if isinstance(result, int):
             next_block_id = result
             if next_block_id:
                  next_block = await self.block_repository.get_by_id(next_block_id)
                  if next_block:
                     return await self._process_block(Block(**next_block.model_dump()), chat_id, user_message, bot_logic, variables)

        else:
            self.logging_client.warning(f"Unsupported block type: {block.type}")
            return None

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
        return None

    async def _safe_execute(
        self,
        handler: Callable[..., Any],
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> Optional[int]:
        """Safely executes a handler with exception handling."""
        try:
            return await handler(content, chat_id, variables, bot_logic, block, user_message)
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
            connection.get("target_block_id")
            for connection in connections
            if connection.get("source_block_id") == block_id
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