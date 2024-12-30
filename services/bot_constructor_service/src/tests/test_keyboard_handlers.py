import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List, Dict, Any
from src.core.logic_manager.handlers.keyboard_handlers import KeyboardHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException
from src.core.logic_manager.base import Block


@pytest.mark.asyncio
async def test_handle_keyboard_success():
    """Test handling keyboard successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = KeyboardHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "keyboard",
        "content": {
              "type": "reply",
             "buttons": [["button1", "button2"], ["button3"]],
        },
    }
    
    await handler.handle_keyboard(block=test_block, chat_id=123, variables={})
    mock_client.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_handle_keyboard_api_error():
    """Test handling keyboard with telegram api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.send_message.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = KeyboardHandler(telegram_client=telegram_client)
    test_block = {
          "id": 1,
        "type": "keyboard",
        "content": {
              "type": "reply",
             "buttons": [["button1", "button2"], ["button3"]],
        },
    }
    with pytest.raises(TelegramAPIException) as exc_info:
        await handler.handle_keyboard(
            block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_handle_keyboard_inline_success():
    """Test handling inline keyboard successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = KeyboardHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "keyboard",
         "content": {
            "type": "inline",
            "buttons": [
                    [{"text": "Button1", "callback_data": "data1"}],
                    [{"text": "Button2", "callback_data": "data2"}]
                 ]
         },
    }
    await handler.handle_keyboard(
         block=test_block, chat_id=123, variables={}
    )
    mock_client.send_message.assert_called_once()