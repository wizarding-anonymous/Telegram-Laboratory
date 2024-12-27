from typing import List
from fastapi import HTTPException
from loguru import logger
from urllib.parse import urlparse

from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name="bot_constructor")


def validate_bot_id(bot_id: int) -> None:
    """Validates the bot ID."""
    if not isinstance(bot_id, int) or bot_id <= 0:
        logging_client.error(f"Invalid bot ID: {bot_id}")
        raise HTTPException(status_code=400, detail="Invalid bot ID")
    logging_client.debug(f"Bot ID: {bot_id} is valid.")


def validate_block_ids(block_ids: List[int]) -> None:
    """Validates a list of block IDs."""
    if not isinstance(block_ids, list) or not all(isinstance(id, int) and id > 0 for id in block_ids):
        logging_client.error(f"Invalid block IDs: {block_ids}")
        raise HTTPException(status_code=400, detail="Invalid block IDs")
    logging_client.debug(f"Block IDs: {block_ids} are valid.")


def validate_block_type(block_type: str) -> None:
    """Validates the block type."""
    allowed_types = [
        "text_message",
        "send_text",
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
        "keyboard",
        "callback_query",
        "inline_query",
        "chat_management",
        "webhook",
        "polling",
        "state_machine",
        "custom_filters",
        "middleware",
        "rate_limiting",
        "error_handling",
        "logging",
        "database",
        "api_request",
        "if_condition",
        "loop",
        "switch_case",
        "wait_for_message",
        "timer",
        "user_data",
         "variable",
         "start",
        
    ]
    if not isinstance(block_type, str) or block_type not in allowed_types:
         logging_client.error(f"Invalid block type: {block_type}")
         raise HTTPException(status_code=400, detail="Invalid block type")
    logging_client.debug(f"Block type: {block_type} is valid.")

def validate_bot_name(bot_name: str) -> None:
    """Validates the bot name."""
    if not isinstance(bot_name, str) or len(bot_name.strip()) < 3 or len(bot_name.strip()) > 255:
        logging_client.error(f"Invalid bot name: {bot_name}")
        raise HTTPException(
            status_code=400, detail="Invalid bot name. Must be between 3 and 255 characters."
        )
    logging_client.debug(f"Bot name: {bot_name} is valid.")


def validate_connections(source_block_id: int, target_block_id: int) -> None:
    """Validates source and target block ids when creating connections."""
    if not isinstance(source_block_id, int) or source_block_id <= 0:
        logging_client.error(f"Invalid source block ID: {source_block_id}")
        raise HTTPException(status_code=400, detail="Invalid source block ID")
    if not isinstance(target_block_id, int) or target_block_id <= 0:
        logging_client.error(f"Invalid target block ID: {target_block_id}")
        raise HTTPException(status_code=400, detail="Invalid target block ID")
    if source_block_id == target_block_id:
         logging_client.error(f"Source and target block IDs must not be the same: source: {source_block_id}, target:{target_block_id}")
         raise HTTPException(status_code=400, detail="Source and target block IDs must not be the same")
    logging_client.debug(f"Connection block IDs are valid. Source ID: {source_block_id}, target ID:{target_block_id}")


def validate_content(content: dict) -> None:
    """Validates the block content (for basic checks only)."""
    if not isinstance(content, dict):
         logging_client.error(f"Invalid content type: {type(content)}. Must be a dictionary.")
         raise HTTPException(status_code=400, detail="Invalid content. Must be a dictionary.")
    logging_client.debug(f"Block content is valid.")


def validate_webhook_url(url: str) -> None:
    """Validates a webhook URL."""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
             logging_client.error(f"Invalid webhook URL: {url}")
             raise HTTPException(status_code=400, detail="Invalid webhook URL")
    except ValueError:
        logging_client.error(f"Invalid webhook URL format: {url}")
        raise HTTPException(status_code=400, detail="Invalid webhook URL format")
    logging_client.debug(f"Webhook URL: {url} is valid.")

def validate_chat_id(chat_id: int) -> None:
    """Validates the chat ID."""
    if not isinstance(chat_id, int) or chat_id <= 0:
        logging_client.error(f"Invalid chat ID: {chat_id}")
        raise HTTPException(status_code=400, detail="Invalid chat ID")
    logging_client.debug(f"Chat ID: {chat_id} is valid.")


def validate_permission(permission: str) -> None:
    """Validates a permission string."""
    if not isinstance(permission, str) or not permission.strip():
         logging_client.error(f"Invalid permission: {permission}")
         raise HTTPException(status_code=400, detail="Invalid permission")
    logging_client.debug(f"Permission: {permission} is valid.")


def validate_user_id(user_id: int) -> None:
    """Validates the user ID."""
    if not isinstance(user_id, int) or user_id <= 0:
        logging_client.error(f"Invalid user ID: {user_id}")
        raise HTTPException(status_code=400, detail="Invalid user ID")
    logging_client.debug(f"User ID: {user_id} is valid.")

def validate_status(status: str) -> None:
    """Validates a status string."""
    allowed_statuses = ["draft", "active", "inactive"]
    if not isinstance(status, str) or status not in allowed_statuses:
        logging_client.error(f"Invalid status: {status}")
        raise HTTPException(status_code=400, detail="Invalid status")
    logging_client.debug(f"Status: {status} is valid.")

def validate_version(version: str) -> None:
    """Validates a version string."""
    if not isinstance(version, str) or not version.strip():
        logging_client.error(f"Invalid version: {version}")
        raise HTTPException(status_code=400, detail="Invalid version")
    logging_client.debug(f"Version: {version} is valid.")