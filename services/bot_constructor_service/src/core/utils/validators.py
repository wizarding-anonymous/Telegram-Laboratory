from typing import List, Any, Dict
from fastapi import HTTPException
from loguru import logger
from urllib.parse import urlparse
import re

from src.integrations.logging_client import LoggingClient
from src.core.utils.exceptions import InvalidContentException
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


def validate_bot_id(bot_id: int) -> None:
    """Validates the bot ID."""
    if not isinstance(bot_id, int) or bot_id <= 0:
        logger.error(f"Invalid bot ID: {bot_id}")
        raise HTTPException(status_code=400, detail="Invalid bot ID")
    logging_client.debug(f"Bot ID: {bot_id} is valid.")


def validate_block_ids(block_ids: List[int]) -> None:
    """Validates a list of block IDs."""
    if not isinstance(block_ids, list) or not all(
        isinstance(id, int) and id > 0 for id in block_ids
    ):
        logger.error(f"Invalid block IDs: {block_ids}")
        raise HTTPException(status_code=400, detail="Invalid block IDs")
    logging_client.debug(f"Block IDs: {block_ids} are valid.")


def validate_block_type(block_type: str) -> None:
    """Validates the block type."""
    allowed_types = [
        "text_message",
        "send_text",
        "keyboard",
        "if_condition",
        "loop",
        "api_request",
        "database_connect",
        "database_query",
        "set_webhook",
        "delete_webhook",
        "handle_callback_query",
        "send_callback_response",
        "variable",
        "try_catch",
        "raise_error",
        "handle_exception",
        "log_message",
        "timer",
        "state_machine",
        "custom_filter",
        "rate_limiting",
        "start",
        "photo_message",
        "video_message",
        "audio_message",
        "document_message",
        "location_message",
        "sticker_message",
        "contact_message",
        "venue_message",
        "game_message",
        "poll_message",
        "send_photo",
        "send_video",
        "send_audio",
        "send_document",
        "send_location",
        "send_sticker",
        "send_contact",
        "send_venue",
        "send_game",
        "send_poll",
        "set_chat_title",
        "set_chat_description",
        "get_chat_members",
        "ban_user",
        "unban_user",
        "pin_message",
        "unpin_message",
        "create_from_template",
        "save_user_data",
        "retrieve_user_data",
        "clear_user_data",
        "manage_session",
        "media_group",
        "flow_chart"
    ]
    if not isinstance(block_type, str) or block_type not in allowed_types:
        logger.error(f"Invalid block type: {block_type}")
        raise HTTPException(status_code=400, detail="Invalid block type")
    logging_client.debug(f"Block type: {block_type} is valid.")


def validate_bot_name(bot_name: str) -> None:
    """Validates the bot name."""
    if not isinstance(bot_name, str) or len(bot_name.strip()) < 3 or len(bot_name.strip()) > 255:
        logger.error(f"Invalid bot name: {bot_name}")
        raise HTTPException(
            status_code=400, detail="Invalid bot name. Must be between 3 and 255 characters."
        )
    logging_client.debug(f"Bot name: {bot_name} is valid.")


def validate_connections(source_block_id: int, target_block_id: int) -> None:
    """Validates source and target block ids when creating connections."""
    if not isinstance(source_block_id, int) or source_block_id <= 0:
        logger.error(f"Invalid source block ID: {source_block_id}")
        raise HTTPException(status_code=400, detail="Invalid source block ID")
    if not isinstance(target_block_id, int) or target_block_id <= 0:
        logger.error(f"Invalid target block ID: {target_block_id}")
        raise HTTPException(status_code=400, detail="Invalid target block ID")
    if source_block_id == target_block_id:
        logger.error(f"Source and target block IDs must not be the same: source: {source_block_id}, target:{target_block_id}")
        raise HTTPException(status_code=400, detail="Source and target block IDs must not be the same")
    logging_client.debug(f"Connection block IDs are valid. Source ID: {source_block_id}, target ID:{target_block_id}")


def validate_content(content: Any) -> None:
    """Validates the block content (for basic checks only)."""
    if not isinstance(content, (dict, str, type(None))) :
        logger.error(f"Invalid content type: {type(content)}. Must be a dictionary, string or None.")
        raise HTTPException(
            status_code=400, detail="Invalid content. Must be a dictionary, string or None."
        )
    logging_client.debug(f"Block content is valid.")


def validate_webhook_url(url: str) -> None:
    """Validates a webhook URL."""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            logger.error(f"Invalid webhook URL: {url}")
            raise HTTPException(status_code=400, detail="Invalid webhook URL")
    except ValueError:
        logger.error(f"Invalid webhook URL format: {url}")
        raise HTTPException(status_code=400, detail="Invalid webhook URL format")
    logging_client.debug(f"Webhook URL: {url} is valid.")


def validate_chat_id(chat_id: int) -> None:
    """Validates the chat ID."""
    if not isinstance(chat_id, int) or chat_id <= 0:
        logger.error(f"Invalid chat ID: {chat_id}")
        raise HTTPException(status_code=400, detail="Invalid chat ID")
    logging_client.debug(f"Chat ID: {chat_id} is valid.")


def validate_permission(permission: str) -> None:
    """Validates a permission string."""
    if not isinstance(permission, str) or not permission.strip():
        logger.error(f"Invalid permission: {permission}")
        raise HTTPException(status_code=400, detail="Invalid permission")
    logging_client.debug(f"Permission: {permission} is valid.")


def validate_user_id(user_id: int) -> None:
    """Validates the user ID."""
    if not isinstance(user_id, int) or user_id <= 0:
        logger.error(f"Invalid user ID: {user_id}")
        raise HTTPException(status_code=400, detail="Invalid user ID")
    logging_client.debug(f"User ID: {user_id} is valid.")


def validate_status(status: str) -> None:
    """Validates a status string."""
    allowed_statuses = ["draft", "active", "inactive"]
    if not isinstance(status, str) or status not in allowed_statuses:
        logger.error(f"Invalid status: {status}")
        raise HTTPException(status_code=400, detail="Invalid status")
    logging_client.debug(f"Status: {status} is valid.")


def validate_version(version: str) -> None:
    """Validates a version string."""
    if not isinstance(version, str) or not version.strip():
        logger.error(f"Invalid version: {version}")
        raise HTTPException(status_code=400, detail="Invalid version")
    logging_client.debug(f"Version: {version} is valid.")

def validate_variable_data(data: Dict[str, Any]) -> None:
    """Validates variable data structure."""
    if not isinstance(data, dict):
        logger.error(f"Invalid variable data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid variable data. Must be a dictionary.")
    if "name" not in data or not isinstance(data["name"], str) or not data["name"].strip():
        logger.error(f"Invalid variable name: {data.get('name')}")
        raise HTTPException(status_code=400, detail="Invalid variable name. Must be a non-empty string.")
    if "action" not in data or not isinstance(data["action"], str) or data["action"] not in ["define", "assign", "retrieve", "update"]:
        logger.error(f"Invalid variable action: {data.get('action')}")
        raise HTTPException(status_code=400, detail="Invalid variable action. Must be define, assign, retrieve or update.")
    logging_client.debug(f"Variable data: {data} is valid.")

def validate_api_request_data(data: Dict[str, Any]) -> None:
    """Validates api request data"""
    if not isinstance(data, dict):
        logger.error(f"Invalid api request data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid api request data. Must be a dictionary.")
    if "url" not in data or not isinstance(data['url'], str) or not data['url'].strip():
         logger.error(f"Invalid api request url: {data.get('url')}")
         raise HTTPException(status_code=400, detail="Invalid api request url. Must be a non-empty string.")
    if "method" not in data or not isinstance(data['method'], str) or data['method'].upper() not in ["GET", "POST", "PUT", "DELETE"]:
         logger.error(f"Invalid api request method: {data.get('method')}")
         raise HTTPException(status_code=400, detail="Invalid api request method. Must be GET, POST, PUT or DELETE")
    if data.get("headers") and not isinstance(data.get('headers'), dict):
        logger.error(f"Invalid headers for api request, headers must be dictionary")
        raise HTTPException(status_code=400, detail="Invalid headers for api request, headers must be dictionary")
    if data.get("params") and not isinstance(data.get('params'), dict):
        logger.error(f"Invalid params for api request, params must be dictionary")
        raise HTTPException(status_code=400, detail="Invalid params for api request, params must be dictionary")
    if data.get("body") and not isinstance(data.get("body"), (dict, str, type(None))):
         logger.error(f"Invalid body for api request, body must be dictionary, string or None")
         raise HTTPException(status_code=400, detail="Invalid body for api request, body must be dictionary, string or None")
    logging_client.debug(f"Api request data is valid.")

def validate_database_data(data: Dict[str, Any]) -> None:
   """Validates database data"""
   if not isinstance(data, dict):
      logger.error(f"Invalid database data: {data}. Must be a dictionary.")
      raise HTTPException(status_code=400, detail="Invalid database data. Must be a dictionary.")
   if "query" not in data or not isinstance(data['query'], str) or not data['query'].strip():
      logger.error(f"Invalid database query: {data.get('query')}")
      raise HTTPException(status_code=400, detail="Invalid database query. Must be a non-empty string.")
   if data.get("params") and not isinstance(data.get("params"), dict):
       logger.error(f"Invalid params for database query, params must be dictionary")
       raise HTTPException(status_code=400, detail="Invalid params for database query, params must be dictionary")
   logging_client.debug(f"Database data is valid")
   
def validate_timer_data(data: Dict[str, Any]) -> None:
    """Validates timer data"""
    if not isinstance(data, dict):
        logger.error(f"Invalid timer data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid timer data. Must be a dictionary.")
    if "delay" not in data or not isinstance(data['delay'], (int, str)):
         logger.error(f"Invalid delay for timer block: {data.get('delay')}")
         raise HTTPException(status_code=400, detail="Invalid delay for timer block, must be int or str")
    logging_client.debug(f"Timer data is valid")

def validate_state_machine_data(data: Dict[str, Any]) -> None:
  """Validates state machine data"""
  if not isinstance(data, dict):
        logger.error(f"Invalid state machine data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid state machine data. Must be a dictionary.")
  if "initial_state" not in data or not isinstance(data['initial_state'], str):
       logger.error(f"Invalid initial state in state machine block: {data.get('initial_state')}")
       raise HTTPException(status_code=400, detail="Invalid state in state machine block. Must be a string.")
  if "transitions" not in data or not isinstance(data['transitions'], list):
       logger.error(f"Invalid transitions in state machine block: {data.get('transitions')}. Must be a list")
       raise HTTPException(status_code=400, detail="Invalid transitions in state machine block, must be a list.")
  for transition in data['transitions']:
    if not isinstance(transition, dict):
      logger.error(f"Invalid transition {transition}, must be a dictionary")
      raise HTTPException(status_code=400, detail="Invalid transition, must be a dictionary")
    if "from_state" not in transition or not isinstance(transition['from_state'], str):
      logger.error(f"Invalid from state: {transition.get('from_state')}")
      raise HTTPException(status_code=400, detail="Invalid from state, must be a string")
    if "to_state" not in transition or not isinstance(transition['to_state'], str):
       logger.error(f"Invalid target state: {transition.get('to_state')}")
       raise HTTPException(status_code=400, detail="Invalid target state, must be a string")
  logging_client.debug(f"State machine data is valid")

def validate_custom_filter_data(data: Dict[str, Any]) -> None:
    """Validates custom filter data"""
    if not isinstance(data, dict):
        logger.error(f"Invalid custom filter data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid custom filter data. Must be a dictionary.")
    if "filter" not in data or not isinstance(data['filter'], str) or not data['filter'].strip():
         logger.error(f"Invalid filter in custom filter block: {data.get('filter')}")
         raise HTTPException(status_code=400, detail="Invalid filter in custom filter block, must be a non empty string.")
    try:
       compile(data["filter"], '<string>', 'eval')
    except SyntaxError:
       logger.error(f"Invalid syntax for filter: {data.get('filter')}")
       raise HTTPException(status_code=400, detail="Invalid syntax for filter, must be valid python syntax")
    logging_client.debug(f"Custom filter data is valid")

def validate_rate_limiting_data(data: Dict[str, Any]) -> None:
    """Validates rate limiting data"""
    if not isinstance(data, dict):
        logger.error(f"Invalid rate limiting data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid rate limiting data. Must be a dictionary.")
    if "limit" not in data or not isinstance(data['limit'], (int, str)):
         logger.error(f"Invalid limit in rate limiting block: {data.get('limit')}")
         raise HTTPException(status_code=400, detail="Invalid limit in rate limiting block, must be int or string.")
    if "interval" not in data or not isinstance(data['interval'], (int, str)):
         logger.error(f"Invalid interval in rate limiting block: {data.get('interval')}")
         raise HTTPException(status_code=400, detail="Invalid interval in rate limiting block, must be int or string")
    logging_client.debug(f"Rate limiting data is valid")

def validate_keyboard_data(data: Dict[str, Any]) -> None:
    """Validates keyboard data."""
    if not isinstance(data, dict):
        logger.error(f"Invalid keyboard data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid keyboard data. Must be a dictionary.")
    if "buttons" not in data or not isinstance(data["buttons"], list):
          logger.error(f"Invalid buttons data: {data.get('buttons')}. Must be a list")
          raise HTTPException(status_code=400, detail="Invalid buttons, must be a list")
    if "type" not in data or not isinstance(data["type"], str) or data["type"] not in ['reply', 'inline']:
        logger.error(f"Invalid keyboard type: {data.get('type')}. Must be 'reply' or 'inline'")
        raise HTTPException(status_code=400, detail="Invalid keyboard type. Must be 'reply' or 'inline'")

    for button in data["buttons"]:
         if not isinstance(button, dict):
              logger.error(f"Invalid keyboard row: {button}. Must be a list.")
              raise HTTPException(status_code=400, detail="Invalid keyboard row. Must be a list.")
         if "text" not in button or not isinstance(button["text"], str) or not button["text"].strip():
              logger.error(f"Invalid button text: {button.get('text')}")
              raise HTTPException(status_code=400, detail="Invalid button text. Must be a non-empty string")
    logging_client.debug(f"Keyboard data is valid")
    
def validate_callback_data(data: Dict[str, Any]) -> None:
    """Validates callback query data."""
    if not isinstance(data, dict):
        logger.error(f"Invalid callback data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid callback data. Must be a dictionary")
    if "data" not in data or not isinstance(data["data"], str) or not data["data"].strip():
        logger.error(f"Invalid callback data: {data.get('data')}")
        raise HTTPException(status_code=400, detail="Invalid callback data. Must be a non-empty string.")
    logging_client.debug(f"Callback data is valid.")

def validate_bot_library(library: str) -> None:
    """Validates the bot library string."""
    allowed_libraries = ["telegram_api", "aiogram", "telebot"]
    if not isinstance(library, str) or library not in allowed_libraries:
         logger.error(f"Invalid bot library: {library}")
         raise HTTPException(status_code=400, detail="Invalid bot library. Must be telegram_api, aiogram or telebot")
    logging_client.debug(f"Bot library: {library} is valid.")

def validate_connection_data(data: Dict[str, Any]) -> None:
    """Validates connection data"""
    if not isinstance(data, dict):
        logger.error(f"Invalid connection data: {data}. Must be a dictionary.")
        raise HTTPException(status_code=400, detail="Invalid connection data. Must be a dictionary.")
    if "source_block_id" not in data or not isinstance(data['source_block_id'], int) or data['source_block_id'] <= 0:
         logger.error(f"Invalid source block id: {data.get('source_block_id')}")
         raise HTTPException(status_code=400, detail="Invalid source block id, must be int and greater than 0")
    if "target_block_id" not in data or not isinstance(data['target_block_id'], int) or data['target_block_id'] <= 0:
         logger.error(f"Invalid target block id: {data.get('target_block_id')}")
         raise HTTPException(status_code=400, detail="Invalid target block id, must be int and greater than 0")
    logging_client.debug(f"Connection data is valid")