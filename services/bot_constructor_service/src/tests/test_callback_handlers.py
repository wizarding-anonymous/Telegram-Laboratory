import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from src.core.logic_manager.handlers.callback_handlers import CallbackHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException
from src.core.logic_manager.base import Block

@pytest.mark.asyncio
async def test_handle_callback_query_success():
    """Test successful callback query handling."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = CallbackHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "handle_callback_query",
        "content": {"data": "test_callback_data"},
    }
    variables = {"variable_test": "test_var"}
    callback_data = await handler.handle_callback_query(
        block=test_block, chat_id=123, variables=variables
    )
    assert callback_data == "test_callback_data"


@pytest.mark.asyncio
async def test_handle_send_callback_response_success():
    """Test send callback response successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = CallbackHandler(telegram_client=mock_client)
    test_block = {
       "id": 1,
        "type": "send_callback_response",
        "content": {"text": "test_callback_text"},
    }
    variables = {"variable_test": "test_var", "callback_query_id": 1}
    await handler.handle_send_callback_response(
      block=test_block, chat_id=123, variables=variables
    )
    mock_client.answer_callback_query.assert_called_once_with(callback_query_id=1, text="test_callback_text")


@pytest.mark.asyncio
async def test_handle_send_callback_response_no_text():
    """Test send callback response with no text."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = CallbackHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "send_callback_response",
         "content": {},
    }
    variables = {"variable_test": "test_var", "callback_query_id": 1}
    await handler.handle_send_callback_response(
        block=test_block, chat_id=123, variables=variables
    )
    mock_client.answer_callback_query.assert_not_called()


@pytest.mark.asyncio
async def test_handle_send_callback_response_api_error():
    """Test send callback response with API error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.answer_callback_query.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = CallbackHandler(telegram_client=telegram_client)
    test_block = {
         "id": 1,
        "type": "send_callback_response",
        "content": {"text": "test_callback_text"},
    }
    variables = {"variable_test": "test_var", "callback_query_id": 1}
    
    with pytest.raises(TelegramAPIException) as exc_info:
          await handler.handle_send_callback_response(
            block=test_block, chat_id=123, variables=variables
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.answer_callback_query.assert_called_once_with(callback_query_id=1, text="test_callback_text")