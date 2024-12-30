import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from src.core.logic_manager.handlers.webhook_handlers import WebhookHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException


@pytest.mark.asyncio
async def test_handle_set_webhook_success():
    """Test setting webhook successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    api_handler = WebhookHandler(telegram_client=mock_client)
    test_block = {
      "id": 1,
        "type": "set_webhook",
        "content": {"url": "https://example.com/webhook"},
    }
    
    await api_handler.handle_set_webhook(
        block=test_block, bot_token="test_token", chat_id=123, variables={}
    )
    mock_client.set_webhook.assert_called_once_with(bot_token="test_token", url="https://example.com/webhook")

@pytest.mark.asyncio
async def test_handle_set_webhook_invalid_url():
    """Test setting webhook with invalid URL."""
    mock_client = AsyncMock(spec=TelegramClient)
    api_handler = WebhookHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
       "type": "set_webhook",
        "content": {"url": "invalid-url"},
    }
    with pytest.raises(HTTPException) as exc_info:
      await api_handler.handle_set_webhook(
         block=test_block, bot_token="test_token", chat_id=123, variables={}
        )
    assert "Invalid webhook URL" in str(exc_info.value.detail)
    mock_client.set_webhook.assert_not_called()
    
@pytest.mark.asyncio
async def test_handle_set_webhook_api_error():
     """Test set webhook with api error."""
     mock_client = AsyncMock(spec=TelegramClient)
     mock_client.set_webhook.side_effect = Exception("Telegram API error")

     test_token = 'test_token'
     telegram_client = TelegramClient(bot_token=test_token)

     api_handler = WebhookHandler(telegram_client=telegram_client)
     test_block = {
          "id": 1,
          "type": "set_webhook",
         "content": {"url": "https://example.com/webhook"},
       }
     with pytest.raises(TelegramAPIException) as exc_info:
          await api_handler.handle_set_webhook(
             block=test_block, bot_token="test_token", chat_id=123, variables={}
        )
     assert "Telegram API error" in str(exc_info.value)
     mock_client.set_webhook.assert_called_once_with(bot_token="test_token", url="https://example.com/webhook")


@pytest.mark.asyncio
async def test_handle_delete_webhook_success():
    """Test delete webhook successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    api_handler = WebhookHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "delete_webhook",
         "content": {},
    }
    await api_handler.handle_delete_webhook(
         block=test_block, bot_token="test_token", chat_id=123, variables={}
    )
    mock_client.delete_webhook.assert_called_once_with(bot_token="test_token")


@pytest.mark.asyncio
async def test_handle_delete_webhook_api_error():
     """Test delete webhook with api error."""
     mock_client = AsyncMock(spec=TelegramClient)
     mock_client.delete_webhook.side_effect = Exception("Telegram API error")
     
     test_token = 'test_token'
     telegram_client = TelegramClient(bot_token=test_token)

     api_handler = WebhookHandler(telegram_client=telegram_client)
     test_block = {
        "id": 1,
        "type": "delete_webhook",
         "content": {},
        }

     with pytest.raises(TelegramAPIException) as exc_info:
          await api_handler.handle_delete_webhook(
            block=test_block, bot_token="test_token", chat_id=123, variables={}
        )
     assert "Telegram API error" in str(exc_info.value)
     mock_client.delete_webhook.assert_called_once_with(bot_token="test_token")