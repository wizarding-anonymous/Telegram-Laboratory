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
        self.handlers: Dict[str, Callable[..., Any]] = {
            "text_message": self._handle_text_message,
            "send_text": self._handle_send_text,
            "keyboard": self._handle_keyboard_block,
            "if_condition": self._handle_if_condition,
            "loop": self._handle_loop_block,
            "api_request": self._handle_api_request_block,
            "database": self._handle_database_block,
            "webhook": self._handle_webhook_block,
            "callback": self._handle_callback_block,
            "variable": self._handle_variable_block,
            "photo_message": self._handle_media_message,
            "video_message": self._handle_media_message,
            "audio_message": self._handle_media_message,
            "document_message": self._handle_media_message,
            "location_message": self._handle_location_message,
            "sticker_message": self._handle_media_message,
            "contact_message": self._handle_contact_message,
            "venue_message": self._handle_venue_message,
            "game_message": self._handle_game_message,
            "poll_message": self._handle_poll_message,
            "send_photo": self._handle_send_media,
            "send_video": self._handle_send_media,
            "send_audio": self._handle_send_media,
            "send_document": self._handle_send_media,
            "send_location": self._handle_send_location,
            "send_sticker": self._handle_send_media,
            "send_contact": self._handle_send_contact,
            "send_venue": self._handle_send_venue,
            "send_game": self._handle_send_game,
            "send_poll": self._handle_send_poll,
            "try_catch": self._handle_try_catch_block,
            "raise_error": self._handle_raise_error_block,
            "handle_exception": self._handle_handle_exception_block,
            "log_message": self._handle_log_message,
            "timer": self._handle_timer_block,
            "state_machine": self._handle_state_machine_block,
            "custom_filter": self._handle_custom_filter_block,
            "rate_limiting": self._handle_rate_limiting_block,
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
                        next_block,
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

    # Общие методы для отправки сообщений

    async def _send_message(
        self,
        chat_id: int,
        message: str,
        reply_markup: Optional[Any] = None,
        inline_keyboard: Optional[Any] = None,
    ) -> None:
        """Sends a message to the specified chat."""
        await self.telegram_client.send_message(
            chat_id, message, reply_markup=reply_markup, inline_keyboard=inline_keyboard
        )

    async def _send_media(
        self,
        chat_id: int,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "photo",
    ) -> None:
        """Sends media to the specified chat."""
        send_method = getattr(self.telegram_client, f"send_{media_type}", None)
        if send_method:
            await send_method(chat_id, media_url, caption=caption)
        else:
            self.logging_client.warning(f"Unsupported media type for sending: {media_type}")

    # Обработчики блоков

    async def _handle_text_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles a text message block."""
        self.logging_client.info(f"Handling text message for chat_id: {chat_id}")
        text_template = content.get("text")
        if text_template:
            text = self.get_template(text_template).render(variables)
            self.logging_client.info(
                f"User sent: {user_message}. Block text: {text}"
            )
            if text in user_message:
                self.logging_client.info("User message matches with content")
                # Do nothing, message is already handled
                return
            else:
                self.logging_client.info("User message does not match with content")

    async def _handle_send_text(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending a text message block."""
        self.logging_client.info(f"Handling send text block for chat_id: {chat_id}")
        text_template = content.get("text")
        if text_template:
            text = self.get_template(text_template).render(variables)
            self.logging_client.info(
                f"Sending text message: {text} to chat_id: {chat_id}"
            )
            await self._send_message(chat_id, text)

    async def _handle_keyboard_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles keyboard block."""
        self.logging_client.info(f"Handling keyboard block for chat_id: {chat_id}")
        keyboard_type = content.get("keyboard_type")
        buttons = content.get("buttons")
        if keyboard_type and buttons:
            rendered_buttons = []
            for row in buttons:
                rendered_row = []
                for button in row:
                    if isinstance(button, dict) and button.get("text"):
                        rendered_text = self.get_template(button["text"]).render(variables)
                        rendered_row.append({
                            "text": rendered_text,
                            "callback_data": button.get("callback_data")
                        })
                    else:
                        rendered_row.append(button)
                rendered_buttons.append(rendered_row)

            if keyboard_type == "reply":
                await self._send_message(
                    chat_id,
                    "Please select option:",
                    reply_markup=rendered_buttons
                )
            elif keyboard_type == "inline":
                await self._send_message(
                    chat_id,
                    "Please select option:",
                    inline_keyboard=rendered_buttons
                )
            else:
                self.logging_client.warning(f"Unsupported keyboard type: {keyboard_type}")

    async def _handle_if_condition(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles if condition block."""
        self.logging_client.info(
            f"Handling if condition block: {block.id} for chat_id: {chat_id}"
        )
        condition_template = content.get("condition")
        if condition_template:
            condition = self.get_template(condition_template).render(variables)
            if condition in user_message:
                self.logging_client.info(
                    f"Condition: {condition} is true for user message: {user_message}. Executing connected blocks."
                )
                # Next blocks are already processed in _process_block
            else:
                self.logging_client.info(
                    f"Condition: {condition} is false for user message: {user_message}. Skipping next blocks."
                )
                # Do nothing, skip next blocks as the condition is not met.

    async def _handle_loop_block(
         self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles loop block."""
        self.logging_client.info(
            f"Handling loop block: {block.id} for chat_id: {chat_id}"
        )

        loop_type = content.get("loop_type")
        loop_count = content.get("count", 0)
        if loop_type == "for":
            try:
                count = int(self.get_template(str(loop_count)).render(variables))
                if count > 0:
                    for i in range(count):
                        self.logging_client.info(
                            f"Executing loop iteration {i + 1} for block: {block.id}"
                        )
                        loop_variables = {**variables, "loop_index": i}
                        next_blocks = await self._get_next_blocks(block.id, bot_logic)
                        if next_blocks:
                            await asyncio.gather(
                                *[
                                    self._process_block(
                                        next_block,
                                        chat_id,
                                        user_message,
                                        bot_logic,
                                        loop_variables,
                                    )
                                    for next_block in next_blocks
                                ]
                            )
                else:
                    self.logging_client.warning("Loop count is less or equals to 0")
            except ValueError:
                self.logging_client.error(
                    f"Can't convert {loop_count} to int"
                )
        elif loop_type == "while":
            condition_template = content.get("condition")
            if condition_template:
                condition = self.get_template(condition_template).render(variables)
                while condition in user_message:
                    self.logging_client.info(
                        f"Executing while loop for block: {block.id} and condition {condition}"
                    )
                    next_blocks = await self._get_next_blocks(block.id, bot_logic)
                    if next_blocks:
                        await asyncio.gather(
                            *[
                                self._process_block(
                                    next_block,
                                    chat_id,
                                    user_message,
                                    bot_logic,
                                    variables,
                                )
                                for next_block in next_blocks
                            ]
                        )
                    condition = self.get_template(condition_template).render(variables)
            else:
                self.logging_client.warning(f"While loop requires condition in {block.id}")

    async def _handle_api_request_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles API request block."""
        self.logging_client.info(f"Handling API request block for chat_id: {chat_id}")
        validate_api_request_data(content)
        url_template = content.get("url")
        method = content.get("method", "GET").lower()
        params = content.get("params", {})
        headers = content.get("headers", {})
        body = content.get("body")

        url = self.get_template(url_template).render(variables)
        api_params = {k: self.get_template(str(v)).render(variables) for k, v in params.items()}
        api_headers = {k: self.get_template(str(v)).render(variables) for k, v in headers.items()}
        api_body = None
        if body and isinstance(body, dict):
            api_body = json.dumps({
                k: self.get_template(str(v)).render(variables) for k, v in body.items()
            })

        self.logging_client.info(
            f"Making API request to url: {url}, method: {method}, params: {api_params}, headers: {api_headers}, body: {api_body}"
        )
        try:
            response = await self.http_client.request(
                method=method,
                url=url,
                params=api_params,
                headers=api_headers,
                content=api_body,
                timeout=10,
            )
            response.raise_for_status()
            self.logging_client.info(
                f"API request successful, response status: {response.status_code}, response: {response.text}"
            )

            response_data = {
                "response": response.text,
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }

            response_block_id = content.get("response_block_id")
            if response_block_id:
                response_block = await self.block_repository.get_by_id(response_block_id)
                if response_block:
                    await self._process_block(
                        Block(**response_block.model_dump()),
                        chat_id,
                        str(response_data),
                        bot_logic,
                        variables,
                    )
                else:
                    self.logging_client.warning(
                        f"Response block with id: {response_block_id} was not found"
                    )
        except httpx.HTTPError as e:
            self.logging_client.error(f"API request failed: {e}")
        except Exception as e:
            self.logging_client.error(f"API request failed: {e}")

    async def _handle_database_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles database request block."""
        self.logging_client.info(f"Handling database request block for chat_id: {chat_id}")
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            self.logging_client.warning("Database query not defined for database block")
            return

        query = self.get_template(query_template).render(variables)
        self.logging_client.info(f"Executing database query: {query}")

        async with get_session() as session:
            try:
                db_params = content.get("params", {})
                rendered_params = {
                    k: self.get_template(str(v)).render(variables)
                    for k, v in db_params.items()
                }
                sql_query = text(query)
                result = await session.execute(sql_query, rendered_params)
                await session.commit()

                if result.rowcount > 0:
                    rows = result.fetchall()
                    formatted_result = [dict(row) for row in rows]
                    self.logging_client.info(f"Database query successful, result: {formatted_result}")
                    response_block_id = content.get("response_block_id")
                    if response_block_id:
                        response_data = {"result": formatted_result}
                        response_block = await self.block_repository.get_by_id(response_block_id)
                        if response_block:
                            await self._process_block(
                                Block(**response_block.model_dump()),
                                chat_id,
                                str(response_data),
                                bot_logic,
                                variables,
                            )
                        else:
                            self.logging_client.warning(
                                f"Response block with id: {response_block_id} was not found"
                            )
                else:
                    self.logging_client.info("Database query successful, no results found.")
            except Exception as e:
                self.logging_client.error(f"Database query failed: {e}")

    async def _handle_webhook_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles webhook block."""
        self.logging_client.info(f"Handling webhook block for chat_id: {chat_id}")
        url_template = content.get("url")
        if not url_template:
            self.logging_client.warning("Webhook url was not defined in webhook block")
            return

        url = self.get_template(url_template).render(variables)
        self.logging_client.info(f"Sending webhook to url: {url}")
        try:
            response = await self.http_client.request(
                url=url,
                method="POST",
                json={"chat_id": chat_id},
            )
            response.raise_for_status()
            self.logging_client.info(f"Webhook was sent successfully, response: {response}")
        except Exception as e:
            self.logging_client.error(f"Webhook was not sent, error: {e}")

    async def _handle_callback_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles callback block."""
        self.logging_client.info(f"Handling callback block for chat_id: {chat_id}")
        callback_data_template = content.get("callback_data")
        if not callback_data_template:
            self.logging_client.warning("Callback data was not defined in callback block")
            return

        callback_data = self.get_template(callback_data_template).render(variables)
        self.logging_client.info(
            f"Callback data: {callback_data}. User message: {user_message}"
        )
        if callback_data in user_message:
            self.logging_client.info(
                f"Callback matches with user message: {user_message}"
            )
            # Do nothing, callback is already handled
            return
        else:
            self.logging_client.info(
                f"Callback does not match with user message"
            )
            return

    async def _handle_variable_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles variable block."""
        self.logging_client.info(f"Handling variable block {block.id}")
        validate_variable_data(content)
        action = content.get('action')
        variable_name = content.get('name')
        if not action or not variable_name:
            self.logging_client.warning("Variable action and name were not provided")
            return

        if action == "define":
            value = content.get("value")
            if value:
                rendered_value = self.get_template(str(value)).render(variables)
                variables[variable_name] = rendered_value
                self.logging_client.info(
                    f"Defining variable: {variable_name} with value: {rendered_value}"
                )
            else:
                variables[variable_name] = None
                self.logging_client.info(
                    f"Defining variable: {variable_name} with value: None"
                )

        elif action == "assign":
            value = content.get("value")
            if value:
                rendered_value = self.get_template(str(value)).render(variables)
                variables[variable_name] = rendered_value
                self.logging_client.info(
                    f"Assigning value: {rendered_value} to variable: {variable_name}"
                )
            else:
                self.logging_client.warning(
                    f"Value for assignment of {variable_name} was not provided"
                )
                return
        elif action == "retrieve":
            retrieved_value = variables.get(variable_name)
            self.logging_client.info(
                f"Retrieving value of variable: {variable_name} and value is {retrieved_value}"
            )
        elif action == "update":
            value = content.get("value")
            if value:
                rendered_value = self.get_template(str(value)).render(variables)
                variables[variable_name] = rendered_value
                self.logging_client.info(
                    f"Updating variable: {variable_name} with value: {rendered_value}"
                )
            else:
                self.logging_client.warning(
                    f"Value for update of {variable_name} was not provided"
                )
                return
        else:
            self.logging_client.warning(f"Unsupported variable action: {action}")

    async def _handle_media_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles various media message blocks."""
        media_type = content.get("type")  # e.g., 'photo', 'video', etc.
        if not media_type:
            self.logging_client.warning("Media type not defined in media message block")
            return

        caption_template = content.get("caption", "")
        if caption_template:
            caption = self.get_template(caption_template).render(variables)
            self.logging_client.info(
                f"User sent: {user_message}. Block caption: {caption}"
            )
        # Дополнительная логика обработки медиа, если требуется

    async def _handle_location_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles a location message block."""
        self.logging_client.info(f"Handling location message for chat_id: {chat_id}")
        latitude_template = content.get("latitude")
        longitude_template = content.get("longitude")
        if latitude_template and longitude_template:
            latitude = self.get_template(str(latitude_template)).render(variables)
            longitude = self.get_template(str(longitude_template)).render(variables)
            self.logging_client.info(
                f"Location received latitude: {latitude}, longitude: {longitude}"
            )

    async def _handle_contact_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles a contact message block."""
        self.logging_client.info(f"Handling contact message for chat_id: {chat_id}")
        phone_number_template = content.get("phone_number")
        if phone_number_template:
            phone_number = self.get_template(phone_number_template).render(variables)
            self.logging_client.info(
                f"User sent contact with number: {phone_number}"
            )

    async def _handle_venue_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles a venue message block."""
        self.logging_client.info(f"Handling venue message for chat_id: {chat_id}")
        address_template = content.get("address")
        if address_template:
            address = self.get_template(address_template).render(variables)
            self.logging_client.info(
                f"User sent venue with address: {address}"
            )

    async def _handle_game_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles a game message block."""
        self.logging_client.info(f"Handling game message for chat_id: {chat_id}")
        game_short_name_template = content.get("game_short_name")
        if game_short_name_template:
            game_short_name = self.get_template(game_short_name_template).render(variables)
            self.logging_client.info(
                f"User sent game with short name: {game_short_name}"
            )

    async def _handle_poll_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles a poll message block."""
        self.logging_client.info(f"Handling poll message for chat_id: {chat_id}")
        question_template = content.get("question")
        if question_template:
            question = self.get_template(question_template).render(variables)
            options = content.get("options", [])
            parsed_options = [
                self.get_template(option).render(variables) for option in options
            ]
            self.logging_client.info(
                f"Sending poll with question: {question} and options: {parsed_options} to chat_id: {chat_id}"
            )
            await self.telegram_client.send_poll(
                chat_id, question, parsed_options
            )

    async def _handle_send_media(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles sending various media types."""
        media_type = content.get("media_type", "photo")
        media_url_template = content.get(f"{media_type}_url")
        caption_template = content.get("caption", "")
        if media_url_template:
            media_url = self.get_template(media_url_template).render(variables)
            caption = self.get_template(caption_template).render(variables) if caption_template else None
            self.logging_client.info(
                f"Sending {media_type} with url: {media_url} to chat_id: {chat_id}"
            )
            await self._send_media(chat_id, media_url, caption, media_type)

    async def _handle_send_location(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending a location message block."""
        self.logging_client.info(f"Handling send location block for chat_id: {chat_id}")
        latitude_template = content.get("latitude")
        longitude_template = content.get("longitude")
        if latitude_template and longitude_template:
            latitude = self.get_template(str(latitude_template)).render(variables)
            longitude = self.get_template(str(longitude_template)).render(variables)
            self.logging_client.info(
                f"Sending location latitude: {latitude} and longitude: {longitude} to chat_id: {chat_id}"
            )
            await self.telegram_client.send_location(
                chat_id, float(latitude), float(longitude)
            )

    async def _handle_send_contact(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending a contact message block."""
        self.logging_client.info(f"Handling send contact block for chat_id: {chat_id}")
        phone_number_template = content.get("phone_number")
        first_name_template = content.get("first_name", "")
        last_name_template = content.get("last_name", "")
        if phone_number_template:
            phone_number = self.get_template(phone_number_template).render(variables)
            first_name = self.get_template(first_name_template).render(variables) if first_name_template else ""
            last_name = self.get_template(last_name_template).render(variables) if last_name_template else ""
            self.logging_client.info(
                f"Sending contact with number: {phone_number} to chat_id: {chat_id}"
            )
            await self.telegram_client.send_contact(
                chat_id, phone_number, first_name, last_name=last_name
            )

    async def _handle_send_venue(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending a venue message block."""
        self.logging_client.info(f"Handling send venue block for chat_id: {chat_id}")
        address_template = content.get("address")
        latitude_template = content.get("latitude", "0")
        longitude_template = content.get("longitude", "0")
        title_template = content.get("title", "")
        if address_template and latitude_template and longitude_template:
            address = self.get_template(address_template).render(variables)
            latitude = self.get_template(str(latitude_template)).render(variables)
            longitude = self.get_template(str(longitude_template)).render(variables)
            title = self.get_template(title_template).render(variables) if title_template else ""
            self.logging_client.info(
                f"Sending venue with address: {address}, latitude: {latitude} and longitude: {longitude} to chat_id: {chat_id}"
            )
            await self.telegram_client.send_venue(
                chat_id, float(latitude), float(longitude), title, address
            )

    async def _handle_send_game(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending a game message block."""
        self.logging_client.info(f"Handling send game block for chat_id: {chat_id}")
        game_short_name_template = content.get("game_short_name")
        if game_short_name_template:
            game_short_name = self.get_template(game_short_name_template).render(variables)
            self.logging_client.info(
                f"Sending game with short name: {game_short_name} to chat_id: {chat_id}"
            )
            await self.telegram_client.send_game(chat_id, game_short_name)

    async def _handle_send_poll(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles sending a poll message block."""
        self.logging_client.info(f"Handling send poll block for chat_id: {chat_id}")
        question_template = content.get("question")
        options = content.get("options", [])
        if question_template and options:
            question = self.get_template(question_template).render(variables)
            parsed_options = [
                self.get_template(option).render(variables) for option in options
            ]
            self.logging_client.info(
                f"Sending poll with question: {question} and options: {parsed_options} to chat_id: {chat_id}"
            )
            await self.telegram_client.send_poll(
                chat_id, question, parsed_options
            )

    async def _handle_try_catch_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles try-catch block."""
        self.logging_client.info(
            f"Handling try-catch block: {block.id} for chat_id: {chat_id}"
        )
        try:
            next_blocks = await self._get_next_blocks(block.id, bot_logic)
            if next_blocks:
                for next_block in next_blocks:
                    await self._process_block(next_block, chat_id, user_message, bot_logic, variables)
        except Exception as e:
            self.logging_client.error(f"An exception occurred in try block: {e}")
            catch_block_id = content.get("catch_block_id")
            if catch_block_id:
                catch_block = await self.block_repository.get_by_id(catch_block_id)
                if catch_block:
                    await self._process_block(Block(**catch_block.model_dump()), chat_id, user_message, bot_logic, variables)
                else:
                    self.logging_client.warning(f"Catch block with id: {catch_block_id} was not found")
            else:
                self.logging_client.warning("Catch block was not defined in try block")
                return

    async def _handle_raise_error_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles raise error block."""
        self.logging_client.info(f"Handling raise error block")
        message_template = content.get("message")
        if message_template:
            message = self.get_template(message_template).render(variables)
            self.logging_client.error(f"Error raised by bot: {message}")
            raise HTTPException(status_code=400, detail=message)
        else:
            self.logging_client.warning("Error message was not provided")

    async def _handle_handle_exception_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles handle exception block."""
        self.logging_client.info(f"Handling handle exception block")
        exception_block_id = content.get("exception_block_id")
        if exception_block_id:
            exception_block = await self.block_repository.get_by_id(exception_block_id)
            if exception_block:
                await self._process_block(Block(**exception_block.model_dump()), chat_id, user_message, bot_logic, variables)
            else:
                self.logging_client.warning(f"Exception block with id: {exception_block_id} was not found")
        else:
            self.logging_client.warning("Exception block was not defined")
            return

    async def _handle_log_message(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles log message block."""
        self.logging_client.info(f"Handling log message block for chat_id: {chat_id}")
        message_template = content.get("message")
        level = content.get("level", "INFO").upper()

        if message_template:
            message = self.get_template(message_template).render(variables)
            if level == "INFO":
                self.logging_client.info(f"Log message: {message}")
            elif level == "DEBUG":
                self.logging_client.debug(f"Log message: {message}")
            elif level == "WARNING":
                self.logging_client.warning(f"Log message: {message}")
            elif level == "ERROR":
                self.logging_client.error(f"Log message: {message}")
            elif level == "CRITICAL":
                self.logging_client.critical(f"Log message: {message}")
            else:
                self.logging_client.warning(f"Unsupported log level: {level}")
                return
        else:
            self.logging_client.warning("Log message or level was not provided")

    async def _handle_timer_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles timer block."""
        self.logging_client.info(f"Handling timer block for chat_id: {chat_id}")
        validate_timer_data(content)
        delay_template = content.get("delay")
        if delay_template:
            try:
                delay = int(self.get_template(str(delay_template)).render(variables))
                if delay > 0:
                    self.logging_client.info(f"Waiting for {delay} seconds")
                    await asyncio.sleep(delay)
                    next_blocks = await self._get_next_blocks(block.id, bot_logic)
                    if next_blocks:
                        await asyncio.gather(
                            *[
                                self._process_block(
                                    next_block,
                                    chat_id,
                                    user_message,
                                    bot_logic,
                                    variables,
                                )
                                for next_block in next_blocks
                            ]
                        )
                else:
                    self.logging_client.warning("Delay is less or equals to 0")
            except ValueError as e:
                self.logging_client.error(f"Can't convert delay to int, error: {e}")
        else:
            self.logging_client.warning("Timer delay was not defined")
            return

    async def _handle_state_machine_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> None:
        """Handles state machine block."""
        self.logging_client.info(
            f"Handling state machine block: {block.id} for chat_id: {chat_id}"
        )
        validate_state_machine_data(content)
        state_template = content.get("state")
        transitions = content.get("transitions", [])
        if state_template and transitions:
            state = self.get_template(state_template).render(variables)
            self.logging_client.info(f"Current state: {state}")
            for transition in transitions:
                trigger_template = transition.get("trigger")
                target_state = transition.get("target_state")
                if trigger_template and target_state:
                    trigger = self.get_template(trigger_template).render(variables)
                    if trigger in user_message:
                        self.logging_client.info(
                            f"Transition triggered by: {trigger}. Moving to state: {target_state}"
                        )
                        # Здесь можно сохранить состояние для последующего использования
                        next_block = await self.block_repository.get_by_id(target_state)
                        if next_block:
                            await self._process_block(Block(**next_block.model_dump()), chat_id, user_message, bot_logic, variables)
                        else:
                            self.logging_client.warning(
                                f"Next block for state: {target_state} was not found"
                            )
                        return
            self.logging_client.warning(f"No transition was triggered from current state {state} and message {user_message}")
            return
        else:
            self.logging_client.warning("State and transitions were not defined")
            return

    async def _handle_custom_filter_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles custom filter block."""
        self.logging_client.info(f"Handling custom filter block for chat_id: {chat_id}")
        validate_custom_filter_data(content)
        filter_expression_template = content.get("filter")
        if filter_expression_template:
            filter_expression = self.get_template(filter_expression_template).render(variables)
            try:
                if eval(filter_expression, {}, variables):
                    self.logging_client.info(f"Custom filter passed: {filter_expression}")
                    next_blocks = await self._get_next_blocks(block.id, bot_logic)
                    if next_blocks:
                        await asyncio.gather(
                            *[
                                self._process_block(
                                    next_block,
                                    chat_id,
                                    user_message,
                                    bot_logic,
                                    variables,
                                )
                                for next_block in next_blocks
                            ]
                        )
                else:
                    self.logging_client.info(f"Custom filter failed: {filter_expression}")
                    return
            except Exception as e:
                self.logging_client.error(f"Custom filter failed with error: {e}")
                return
        else:
            self.logging_client.warning("Custom filter was not defined")

    async def _handle_rate_limiting_block(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> None:
        """Handles rate limiting block."""
        self.logging_client.info(f"Handling rate limiting block for chat_id: {chat_id}")
        validate_rate_limiting_data(content)
        limit_template = content.get("limit")
        interval_template = content.get("interval")
        if limit_template and interval_template:
            try:
                limit = int(self.get_template(str(limit_template)).render(variables))
                interval = int(self.get_template(str(interval_template)).render(variables))
                cache_key = f"rate_limit:{chat_id}:{block.id}"
                current_count = await redis_client.get(cache_key)
                current_count = int(current_count) if current_count else 0

                if current_count < limit:
                    await redis_client.setex(cache_key, interval, current_count + 1)
                    self.logging_client.info(
                        f"Rate limit passed, current count: {current_count + 1}"
                    )
                    next_blocks = await self._get_next_blocks(block.id, bot_logic)
                    if next_blocks:
                        await asyncio.gather(
                            *[
                                self._process_block(
                                    next_block,
                                    chat_id,
                                    user_message,
                                    bot_logic,
                                    variables,
                                )
                                for next_block in next_blocks
                            ]
                        )
                else:
                    self.logging_client.warning(
                        f"Rate limit exceeded, current count: {current_count}"
                    )
            except ValueError as e:
                self.logging_client.error(f"Can't convert limit or interval to int, error: {e}")
            except Exception as e:
                self.logging_client.error(f"Error with rate limiting, error: {e}")
        else:
            self.logging_client.warning("Rate limit or interval was not defined")
            return

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