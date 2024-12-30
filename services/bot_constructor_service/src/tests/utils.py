import json
from typing import Dict, Any

from src.db.models import Block, Bot


def create_test_block(**kwargs: Any) -> Block:
    """Creates a test block with default values."""
    default_values = {
        "id": 1,
        "bot_id": 1,
        "type": "text_message",
        "content": {"text": "test"},
        "connections": [],
        "created_at": None,
        "updated_at": None,
        "user_message_id": None,
        "bot_message_id": None,
    }
    default_values.update(kwargs)
    return Block(**default_values)


def create_test_bot(**kwargs: Any) -> Bot:
    """Creates a test bot with default values."""
    default_values = {
        "id": 1,
        "user_id": 1,
        "name": "Test Bot",
        "description": "Test description",
        "status": "draft",
        "version": "1.0.0",
        "created_at": None,
        "updated_at": None,
        "logic": {"start_block_id": 1},
         "token": "test_token",
         "library": "telegram_api"
    }
    default_values.update(kwargs)
    return Bot(**default_values)