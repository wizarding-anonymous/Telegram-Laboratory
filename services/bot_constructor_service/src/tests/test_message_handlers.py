import pytest
from unittest.mock import AsyncMock

from src.core.logic_manager.handlers.message_handlers import TextMessageBlockHandler, MediaMessageBlockHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException
from src.core.logic_manager.base import Block


@pytest.mark.asyncio
async def test_handle_text_message_success():
    """Test send text message successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = TextMessageBlockHandler(telegram_client=mock_client)
    test_block = {
       "id": 1,
        "type": "send_text",
        "content": {"text": "test_message"},
    }
    await handler.handle_send_text(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.send_message.assert_called_once_with(chat_id=123, text="test_message", parse_mode="HTML", reply_markup=None, inline_keyboard=None)


@pytest.mark.asyncio
async def test_handle_text_message_api_error():
    """Test send text message with telegram api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.send_message.side_effect = Exception("Telegram API error")

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = TextMessageBlockHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
        "type": "send_text",
        "content": {"text": "test_message"},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
        await handler.handle_send_text(
            block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.send_message.assert_called_once_with(chat_id=123, text="test_message", parse_mode="HTML", reply_markup=None, inline_keyboard=None)

@pytest.mark.asyncio
async def test_handle_media_message_success():
    """Test send media message successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaMessageBlockHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "send_photo",
        "content": {"media": "test_photo_url", "caption": "test_caption"},
    }
    await handler.handle_send_media(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.send_photo.assert_called_once_with(chat_id=123, photo="test_photo_url", caption="test_caption")

@pytest.mark.asyncio
async def test_handle_media_message_api_error():
    """Test send media message with telegram api error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.send_photo.side_effect = Exception("Telegram API error")
    
    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = MediaMessageBlockHandler(telegram_client=telegram_client)
    test_block = {
       "id": 1,
        "type": "send_photo",
        "content": {"media": "test_photo_url", "caption": "test_caption"},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
       await handler.handle_send_media(
            block=test_block, chat_id=123, variables={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.send_photo.assert_called_once_with(chat_id=123, photo="test_photo_url", caption="test_caption")

@pytest.mark.asyncio
async def test_handle_media_message_no_content():
    """Test send media message with no content."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaMessageBlockHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "send_photo",
        "content": {},
    }
    with pytest.raises(HTTPException) as exc_info:
        await handler.handle_send_media(
            block=test_block, chat_id=123, variables={}
        )
    assert "Content was not provided" in str(exc_info.value.detail)
    mock_client.send_photo.assert_not_called()


@pytest.mark.asyncio
async def test_handle_text_message_with_variables():
    """Test send text message with variables."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = TextMessageBlockHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "send_text",
        "content": {"text": "Hello, {{name}}!"},
    }
    variables = {"name": "Test"}
    await handler.handle_send_text(
        block=test_block, chat_id=123, variables=variables
    )
    mock_client.send_message.assert_called_once_with(chat_id=123, text="Hello, Test!", parse_mode="HTML", reply_markup=None, inline_keyboard=None)

@pytest.mark.asyncio
async def test_handle_send_location():
    """Test send location message."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaMessageBlockHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "send_location",
         "content": {"latitude": 10.0, "longitude": 20.0},
    }
    await handler.handle_send_location(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.send_location.assert_called_once_with(chat_id=123, latitude=10.0, longitude=20.0)

@pytest.mark.asyncio
async def test_handle_send_contact():
    """Test send contact message."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaMessageBlockHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "send_contact",
        "content": {"phone_number": "123-456-7890", "first_name": "John"},
    }
    await handler.handle_send_contact(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.send_contact.assert_called_once_with(chat_id=123, phone_number="123-456-7890", first_name="John", last_name="")


@pytest.mark.asyncio
async def test_handle_send_venue():
    """Test send venue message."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaMessageBlockHandler(telegram_client=mock_client)
    test_block = {
       "id": 1,
        "type": "send_venue",
        "content": {"latitude": 10.0, "longitude": 20.0, "title": "Test Venue", "address": "Test Address"},
    }
    await handler.handle_send_venue(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.send_venue.assert_called_once_with(chat_id=123, latitude=10.0, longitude=20.0, title="Test Venue", address="Test Address")

@pytest.mark.asyncio
async def test_handle_send_game():
        """Test send game message."""
        mock_client = AsyncMock(spec=TelegramClient)
        handler = MediaMessageBlockHandler(telegram_client=mock_client)
        test_block = {
           "id": 1,
            "type": "send_game",
            "content": {"game_short_name": "test_game"},
        }
        await handler.handle_send_game(
            block=test_block, chat_id=123, variables={}
        )
        mock_client.send_game.assert_called_once_with(chat_id=123, game_short_name="test_game")

@pytest.mark.asyncio
async def test_handle_send_poll():
    """Test send poll message."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaMessageBlockHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "send_poll",
        "content": {"question": "test_question", "options": ["test_option_1", "test_option_2"]},
    }
    await handler.handle_send_poll(
        block=test_block, chat_id=123, variables={}
    )
    mock_client.send_poll.assert_called_once_with(chat_id=123, question="test_question", options=["test_option_1", "test_option_2"])