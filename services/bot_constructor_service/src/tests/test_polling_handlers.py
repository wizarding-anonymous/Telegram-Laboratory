import pytest
from unittest.mock import AsyncMock, MagicMock

from src.core.logic_manager.handlers.polling_handlers import PollingHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException


@pytest.mark.asyncio
async def test_handle_start_polling_success():
    """Test start polling successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = PollingHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "start_polling",
        "content": {},
    }
    await handler.handle_start_polling(
        block=test_block, bot_token="test_token", chat_id=123, variables={}
    )
    mock_client.start_polling.assert_called_once_with(bot_token="test_token")


@pytest.mark.asyncio
async def test_handle_start_polling_api_error():
    """Test start polling with API error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.start_polling.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = PollingHandler(telegram_client=telegram_client)
    test_block = {
          "id": 1,
        "type": "start_polling",
        "content": {},
       }
    with pytest.raises(TelegramAPIException) as exc_info:
         await handler.handle_start_polling(
             block=test_block, bot_token="test_token", chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.start_polling.assert_called_once_with(bot_token="test_token")


@pytest.mark.asyncio
async def test_handle_stop_polling_success():
    """Test stop polling successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = PollingHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "stop_polling",
        "content": {},
    }
    await handler.handle_stop_polling(
        block=test_block, bot_token="test_token", chat_id=123, variables={}
    )
    mock_client.stop_polling.assert_called_once_with(bot_token="test_token")


@pytest.mark.asyncio
async def test_handle_stop_polling_api_error():
    """Test stop polling with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.stop_polling.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = PollingHandler(telegram_client=telegram_client)
    test_block = {
      "id": 1,
      "type": "stop_polling",
      "content": {},
       }
    with pytest.raises(TelegramAPIException) as exc_info:
         await handler.handle_stop_polling(
             block=test_block, bot_token="test_token", chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.stop_polling.assert_called_once_with(bot_token="test_token")