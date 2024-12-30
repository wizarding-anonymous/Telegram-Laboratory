import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from src.core.logic_manager.handlers.chat_handlers import ChatHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException


@pytest.mark.asyncio
async def test_handle_get_chat_members_success():
    """Test get chat members successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.get_chat_members.return_value = [{"user_id": 1, "name": "Test User"}]
    handler = ChatHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "get_chat_members",
         "content": {},
    }
    chat_members = await handler.handle_get_chat_members(
         block=test_block, chat_id=123, variables={}
    )
    assert chat_members == [{"user_id": 1, "name": "Test User"}]
    mock_client.get_chat_members.assert_called_once_with(chat_id=123)

@pytest.mark.asyncio
async def test_handle_get_chat_members_api_error():
    """Test get chat members with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.get_chat_members.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
        "type": "get_chat_members",
        "content": {},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
         await handler.handle_get_chat_members(
            block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.get_chat_members.assert_called_once_with(chat_id=123)


@pytest.mark.asyncio
async def test_handle_ban_user_success():
    """Test ban user successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = ChatHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "ban_user",
         "content": {"user_id": 456},
    }
    await handler.handle_ban_user(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.ban_chat_member.assert_called_once_with(chat_id=123, user_id=456)

@pytest.mark.asyncio
async def test_handle_ban_user_api_error():
    """Test ban user with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.ban_chat_member.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
        "type": "ban_user",
         "content": {"user_id": 456},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
       await handler.handle_ban_user(
            block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.ban_chat_member.assert_called_once_with(chat_id=123, user_id=456)
    

@pytest.mark.asyncio
async def test_handle_unban_user_success():
    """Test unban user successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = ChatHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "unban_user",
         "content": {"user_id": 456},
    }
    await handler.handle_unban_user(
      block=test_block, chat_id=123, variables={}
    )
    mock_client.unban_chat_member.assert_called_once_with(chat_id=123, user_id=456)

@pytest.mark.asyncio
async def test_handle_unban_user_api_error():
    """Test unban user with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.unban_chat_member.side_effect = Exception("Telegram API error")
    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
        "type": "unban_user",
        "content": {"user_id": 456},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
        await handler.handle_unban_user(
           block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.unban_chat_member.assert_called_once_with(chat_id=123, user_id=456)


@pytest.mark.asyncio
async def test_handle_set_chat_title_success():
    """Test setting chat title successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = ChatHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "set_chat_title",
         "content": {"title": "test_title"},
    }
    await handler.handle_set_chat_title(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.set_chat_title.assert_called_once_with(chat_id=123, title="test_title")

@pytest.mark.asyncio
async def test_handle_set_chat_title_api_error():
    """Test set chat title with API error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.set_chat_title.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)
    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
       "type": "set_chat_title",
       "content": {"title": "test_title"},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
        await handler.handle_set_chat_title(
            block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.set_chat_title.assert_called_once_with(chat_id=123, title="test_title")

@pytest.mark.asyncio
async def test_handle_set_chat_description_success():
    """Test setting chat description successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = ChatHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "set_chat_description",
        "content": {"description": "test_description"},
    }
    await handler.handle_set_chat_description(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.set_chat_description.assert_called_once_with(chat_id=123, description="test_description")


@pytest.mark.asyncio
async def test_handle_set_chat_description_api_error():
    """Test set chat description with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.set_chat_description.side_effect = Exception("Telegram API error")
    
    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
         "id": 1,
        "type": "set_chat_description",
         "content": {"description": "test_description"},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
          await handler.handle_set_chat_description(
             block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.set_chat_description.assert_called_once_with(chat_id=123, description="test_description")


@pytest.mark.asyncio
async def test_handle_pin_message_success():
     """Test pin message successfully."""
     mock_client = AsyncMock(spec=TelegramClient)
     handler = ChatHandler(telegram_client=mock_client)
     test_block = {
        "id": 1,
         "type": "pin_message",
        "content": {"message_id": 789}
    }
     await handler.handle_pin_message(
        block=test_block, chat_id=123, variables={}
    )
     mock_client.pin_chat_message.assert_called_once_with(chat_id=123, message_id=789)

@pytest.mark.asyncio
async def test_handle_pin_message_api_error():
    """Test pin message with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.pin_chat_message.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
        "type": "pin_message",
         "content": {"message_id": 789}
    }
    with pytest.raises(TelegramAPIException) as exc_info:
          await handler.handle_pin_message(
           block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.pin_chat_message.assert_called_once_with(chat_id=123, message_id=789)


@pytest.mark.asyncio
async def test_handle_unpin_message_success():
     """Test unpin message successfully."""
     mock_client = AsyncMock(spec=TelegramClient)
     handler = ChatHandler(telegram_client=mock_client)
     test_block = {
        "id": 1,
        "type": "unpin_message",
         "content": {"message_id": 789}
    }
     await handler.handle_unpin_message(
        block=test_block, chat_id=123, variables={}
    )
     mock_client.unpin_chat_message.assert_called_once_with(chat_id=123, message_id=789)

@pytest.mark.asyncio
async def test_handle_unpin_message_api_error():
    """Test unpin message with api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.unpin_chat_message.side_effect = Exception("Telegram API error")
    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = ChatHandler(telegram_client=telegram_client)
    test_block = {
         "id": 1,
        "type": "unpin_message",
         "content": {"message_id": 789}
    }
    with pytest.raises(TelegramAPIException) as exc_info:
        await handler.handle_unpin_message(
           block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.unpin_chat_message.assert_called_once_with(chat_id=123, message_id=789)
    