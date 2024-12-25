# services\bot_constructor_service\src\core\utils\validators.py
"""
Validators Module

This module contains validation functions to ensure the integrity and correctness of data
within the bot_constructor_service. These validators are used in Pydantic models and
other parts of the application to enforce business rules and data constraints.
"""

from typing import List, Optional
from pydantic import ValidationError

# Define custom exceptions if needed
class BlockValidationError(ValidationError):
    """Custom exception for block validation errors."""
    pass

def validate_block_type(block_type: str) -> str:
    """
    Validate the type of a block.

    Args:
        block_type (str): The type of the block to validate.

    Returns:
        str: The validated block type.

    Raises:
        BlockValidationError: If the block type is invalid.
    """
    valid_types = ["message", "action", "logic"]
    if block_type not in valid_types:
        raise BlockValidationError(
            errors=[{
                "loc": ("type",),
                "msg": f"Invalid block type: '{block_type}'. Must be one of {valid_types}.",
                "type": "value_error"
            }],
            model=None
        )
    return block_type

def validate_connections(connections: Optional[List[int]]) -> List[int]:
    """
    Validate the connections of a block.

    Args:
        connections (Optional[List[int]]): A list of block IDs that the current block connects to.

    Returns:
        List[int]: The validated list of block IDs.

    Raises:
        BlockValidationError: If any block ID is invalid.
    """
    if connections is None:
        return []
    
    if not isinstance(connections, list):
        raise BlockValidationError(
            errors=[{
                "loc": ("connections",),
                "msg": "Connections must be a list of block IDs.",
                "type": "type_error.list"
            }],
            model=None
        )
    
    for idx, block_id in enumerate(connections):
        if not isinstance(block_id, int) or block_id <= 0:
            raise BlockValidationError(
                errors=[{
                    "loc": ("connections", idx),
                    "msg": f"Invalid block ID: {block_id}. Must be a positive integer.",
                    "type": "value_error"
                }],
                model=None
            )
    return connections

def validate_bot_id(bot_id: int) -> int:
    """
    Validate the bot ID.

    Args:
        bot_id (int): The ID of the bot to validate.

    Returns:
        int: The validated bot ID.

    Raises:
        BlockValidationError: If the bot ID is invalid.
    """
    if not isinstance(bot_id, int) or bot_id <= 0:
        raise BlockValidationError(
            errors=[{
                "loc": ("bot_id",),
                "msg": f"Invalid bot ID: {bot_id}. Must be a positive integer.",
                "type": "value_error"
            }],
            model=None
        )
    return bot_id

def validate_bot_name(name: str) -> str:
    """
    Validate the name of the bot.

    Args:
        name (str): The name of the bot to validate.

    Returns:
        str: The validated bot name.

    Raises:
        BlockValidationError: If the bot name is invalid.
    """
    if not isinstance(name, str):
        raise BlockValidationError(
            errors=[{
                "loc": ("name",),
                "msg": "Bot name must be a string.",
                "type": "type_error.str"
            }],
            model=None
        )
    
    if not name.strip():
        raise BlockValidationError(
            errors=[{
                "loc": ("name",),
                "msg": "Bot name cannot be empty.",
                "type": "value_error.empty"
            }],
            model=None
        )
    
    if len(name) > 255:
        raise BlockValidationError(
            errors=[{
                "loc": ("name",),
                "msg": "Bot name cannot exceed 255 characters.",
                "type": "value_error"
            }],
            model=None
        )
    
    return name

def validate_content(content: dict) -> dict:
    """
    Validate the content of a block.

    Args:
        content (dict): The content of the block to validate.

    Returns:
        dict: The validated content.

    Raises:
        BlockValidationError: If the content is invalid.
    """
    if not isinstance(content, dict):
        raise BlockValidationError(
            errors=[{
                "loc": ("content",),
                "msg": "Content must be a dictionary.",
                "type": "type_error.dict"
            }],
            model=None
        )
    
    # Add more specific validations based on block type if necessary
    return content


def validate_status(status: str) -> str:
    """
    Validate the status of a bot.

    Args:
        status (str): The status of the bot to validate.

    Returns:
        str: The validated status.

    Raises:
        BlockValidationError: If the status is invalid.
    """
    valid_statuses = ["active", "inactive", "paused"]
    if status not in valid_statuses:
        raise BlockValidationError(
            errors=[{
                "loc": ("status",),
                "msg": f"Invalid status: '{status}'. Must be one of {valid_statuses}.",
                "type": "value_error"
            }],
            model=None
        )
    return status


def validate_version(version: str) -> str:
    """
    Validate the version string for the bot.

    Args:
        version (str): The version string to validate.

    Returns:
        str: The validated version string.

    Raises:
        BlockValidationError: If the version string is invalid.
    """
    if not isinstance(version, str):
        raise BlockValidationError(
            errors=[{
                "loc": ("version",),
                "msg": "Version must be a string.",
                "type": "type_error.str"
            }],
            model=None
        )

    # Example version validation: Simple semantic versioning
    version_pattern = r"^\d+\.\d+\.\d+$"
    if not re.match(version_pattern, version):
        raise BlockValidationError(
            errors=[{
                "loc": ("version",),
                "msg": f"Invalid version format: '{version}'. Must follow 'X.Y.Z' format.",
                "type": "value_error"
            }],
            model=None
        )
    return version


def validate_webhook_url(webhook_url: str) -> str:
    """
    Validate the webhook URL for Telegram integration.

    Args:
        webhook_url (str): The webhook URL to validate.

    Returns:
        str: The validated webhook URL.

    Raises:
        BlockValidationError: If the webhook URL is invalid.
    """
    import re

    url_pattern = re.compile(
        r'^(https?://)?'  
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})' 
        r'(:\d+)?'  
        r'(\/.*)?$'  
    )
    if not isinstance(webhook_url, str) or not url_pattern.match(webhook_url):
        raise BlockValidationError(
            errors=[{
                "loc": ("webhook_url",),
                "msg": f"Invalid webhook URL: '{webhook_url}'. Must be a valid URL.",
                "type": "value_error.url"
            }],
            model=None
        )
    return webhook_url

def validate_chat_id(chat_id: int) -> int:
    """
    Validate the Telegram chat ID.

    Args:
        chat_id (int): The Telegram chat ID to validate.

    Returns:
        int: The validated chat ID.

    Raises:
        BlockValidationError: If the chat ID is invalid.
    """
    if not isinstance(chat_id, int) or chat_id <= 0:
        raise BlockValidationError(
            errors=[{
                "loc": ("chat_id",),
                "msg": f"Invalid chat ID: {chat_id}. Must be a positive integer.",
                "type": "value_error"
            }],
            model=None
        )
    return chat_id

def validate_permission(permission: str) -> str:
    """
    Validate user permissions.

    Args:
        permission (str): The permission string to validate.

    Returns:
        str: The validated permission string.

    Raises:
        BlockValidationError: If the permission is invalid.
    """
    valid_permissions = ["create_bot", "edit_bot", "delete_bot", "view_bot"]
    if permission not in valid_permissions:
        raise BlockValidationError(
            errors=[{
                "loc": ("permission",),
                "msg": f"Invalid permission: '{permission}'. Must be one of {valid_permissions}.",
                "type": "value_error"
            }],
            model=None
        )
    return permission

def validate_user_id(user_id: int) -> int:
    """
    Validate the user ID.

    Args:
        user_id (int): The ID of the user to validate.

    Returns:
        int: The validated user ID.

    Raises:
        BlockValidationError: If the user ID is invalid.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise BlockValidationError(
            errors=[{
                "loc": ("user_id",),
                "msg": f"Invalid user ID: {user_id}. Must be a positive integer.",
                "type": "value_error"
            }],
            model=None
        )
    return user_id

def validate_block_ids(block_ids: List[int]) -> List[int]:
    """
    Validate a list of block IDs.

    Args:
        block_ids (List[int]): A list of block IDs to validate.

    Returns:
        List[int]: The validated list of block IDs.

    Raises:
        BlockValidationError: If any block ID is invalid.
    """
    if not isinstance(block_ids, list):
        raise BlockValidationError(
            errors=[{
                "loc": ("block_ids",),
                "msg": "Block IDs must be provided as a list.",
                "type": "type_error.list"
            }],
            model=None
        )
    
    for idx, block_id in enumerate(block_ids):
        if not isinstance(block_id, int) or block_id <= 0:
            raise BlockValidationError(
                errors=[{
                    "loc": ("block_ids", idx),
                    "msg": f"Invalid block ID: {block_id}. Must be a positive integer.",
                    "type": "value_error"
                }],
                model=None
            )
    return block_ids

# Additional validators as needed for the business logic
