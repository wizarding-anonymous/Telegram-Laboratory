import json
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException
from sqlalchemy import text

from src.core.utils import handle_exceptions
from src.core.utils.validators import (
    validate_api_request_data,
    validate_database_data,
    validate_webhook_url,
)
from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.db.database import get_session
from src.db.repositories import BlockRepository
from src.core.logic_manager.base import Block
from src.integrations.telegram import TelegramClient
from src.config import settings
logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class ApiRequestHandler:
    """
    Handler for processing API request blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_api_request(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
        block: Block,
    ) -> Optional[int]:
        """Handles API request block."""
        logging_client.info(f"Handling API request block for chat_id: {chat_id}")
        validate_api_request_data(content)
        url_template = content.get("url")
        method = content.get("method", "GET").lower()
        params = content.get("params", {})
        headers = content.get("headers", {})
        body = content.get("body")

        url = get_template(url_template).render(variables=variables)
        api_params = {
            k: get_template(str(v)).render(variables=variables)
            for k, v in params.items()
        }
        api_headers = {
            k: get_template(str(v)).render(variables=variables)
            for k, v in headers.items()
        }
        api_body = None
        if body and isinstance(body, dict):
            api_body = json.dumps(
                {
                    k: get_template(str(v)).render(variables=variables)
                    for k, v in body.items()
                }
            )
        logging_client.info(
           f"Making API request to url: {url}, method: {method}, params: {api_params}, headers: {api_headers}, body: {api_body}. User message was: {user_message}"
        )
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=api_params,
                    headers=api_headers,
                    content=api_body,
                    timeout=10,
                )
                response.raise_for_status()
                logging_client.info(
                    f"API request successful, response status: {response.status_code}, response: {response.text}"
                )

                response_data = {
                    "response": response.text,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }

                response_block_id = content.get("response_block_id")
                if response_block_id:
                     from src.core.logic_manager import LogicManager
                     logic_manager = LogicManager()
                     from src.db.repositories import BlockRepository
                     block_repository = BlockRepository()
                     response_block = await block_repository.get_by_id(response_block_id)
                     if response_block:
                         await logic_manager._process_block(
                                 Block(**response_block.model_dump()),
                                  chat_id,
                                  str(response_data),
                                  bot_logic,
                                  variables,
                             )
                         return None
                     else:
                         logging_client.warning(
                            f"Response block with id: {response_block_id} was not found"
                        )
            except httpx.HTTPError as e:
                logging_client.error(f"API request failed: {e}")
                raise
            except Exception as e:
                 logging_client.error(f"API request failed: {e}")
                 raise
        return None


class DatabaseHandler:
    """
    Handler for processing database request blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_database_connect(self, content: Dict[str, Any], chat_id: int, variables: Dict[str,Any], block: Block) -> None:
         """Handles database connect block."""
         logging_client.info(f"Handling database connect block for chat_id: {chat_id}")
         validate_database_data(content)
         # For now just log the event
         connection_params = content.get("connection_params", {})
         rendered_params = {
             k: get_template(str(v)).render(variables=variables)
             for k, v in connection_params.items()
         }
         logging_client.info(f"Connecting to database with params {rendered_params}")
         return None
    
    @handle_exceptions
    async def handle_database_query(
        self,
        content: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
         block: Block,
    ) -> Optional[int]:
        """Handles database request block."""
        logging_client.info(f"Handling database request block for chat_id: {chat_id}. User message was: {user_message}")
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            logging_client.warning("Database query not defined for database block")
            return None
        query = get_template(query_template).render(variables=variables)
        logging_client.info(f"Executing database query: {query}")
        async with get_session() as session:
            try:
                db_params = content.get("params", {})
                rendered_params = {
                    k: get_template(str(v)).render(variables=variables)
                    for k, v in db_params.items()
                }
                sql_query = text(query)
                result = await session.execute(sql_query, rendered_params)
                await session.commit()
                if result.rowcount > 0:
                    rows = result.fetchall()
                    formatted_result = [dict(row) for row in rows]
                    logging_client.info(f"Database query successful, result: {formatted_result}")
                    response_block_id = content.get("response_block_id")
                    if response_block_id:
                        from src.core.logic_manager.base import Block
                        from src.core.logic_manager import LogicManager
                        logic_manager = LogicManager()
                        from src.db.repositories import BlockRepository
                        block_repository = BlockRepository()
                        response_block = await block_repository.get_by_id(response_block_id)
                        if response_block:
                           await logic_manager._process_block(
                                  Block(**response_block.model_dump()),
                                  chat_id,
                                   str({"result": formatted_result}),
                                   bot_logic,
                                   variables,
                               )
                           return None
                        else:
                           logging_client.warning(
                              f"Response block with id: {response_block_id} was not found"
                            )
                else:
                    logging_client.info("Database query successful, no results found.")
            except Exception as e:
                logging_client.error(f"Database query failed: {e}")
        return None

class WebhookHandler:
    """
    Handler for processing webhook blocks.
    """
    def __init__(self, telegram_client: TelegramClient):
        self.telegram_client = telegram_client

    @handle_exceptions
    async def handle_set_webhook(self, content: Dict[str, Any], chat_id: int, variables: Dict[str,Any], bot_token: str) -> None:
        """Handles webhook block."""
        logging_client.info(f"Handling webhook block for chat_id: {chat_id}")
        url_template = content.get("url")
        if not url_template:
            logging_client.warning("Webhook url was not defined in webhook block")
            return

        url = get_template(url_template).render(variables=variables)
        validate_webhook_url(url)
        logging_client.info(f"Setting webhook to url: {url}")
        try:
             await self.telegram_client.set_webhook(bot_token=bot_token, url=url)
             logging_client.info(f"Webhook was set successfully, url: {url}")
        except Exception as e:
            logging_client.error(f"Webhook was not set, error: {e}")
            raise
    
    @handle_exceptions
    async def handle_delete_webhook(self, content: Dict[str, Any], chat_id: int, variables: Dict[str,Any], bot_token: str) -> None:
        """Handles webhook block."""
        logging_client.info(f"Handling delete webhook block for chat_id: {chat_id}")
        try:
             await self.telegram_client.delete_webhook(bot_token=bot_token)
             logging_client.info(f"Webhook was deleted successfully")
        except Exception as e:
            logging_client.error(f"Webhook was not deleted, error: {e}")
            raise