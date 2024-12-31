import pytest
from unittest.mock import AsyncMock
from src.integrations.telegram import TelegramAPI
from httpx import AsyncClient
from typing import Dict, Any
from src.core.utils.exceptions import TelegramAPIException


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """
    Fixture to create a mock httpx AsyncClient.
    """
    mock = AsyncMock(spec=AsyncClient)
    return mock


@pytest.fixture
def telegram_api_client(mock_httpx_client: AsyncMock) -> TelegramAPI:
    """
    Fixture to create a TelegramAPI client with a mock httpx client.
    """
    return TelegramAPI(token="test_token", client=mock_httpx_client)


@pytest.mark.asyncio
async def test_send_message_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful sending of a message.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )

    response = await telegram_api_client.send_message(chat_id=123, text="Test message")
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test sending of a message with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.send_message(chat_id=123, text="Test message")
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_send_reply_keyboard_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful sending of a reply keyboard.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    buttons = [{"text": "button1"}, {"text": "button2"}]
    response = await telegram_api_client.send_reply_keyboard(
        chat_id=123, buttons=buttons
    )
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_send_reply_keyboard_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
     Test sending of a reply keyboard with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    buttons = [{"text": "button1"}, {"text": "button2"}]
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.send_reply_keyboard(chat_id=123, buttons=buttons)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_send_inline_keyboard_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
     Test successful sending of an inline keyboard.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    buttons = [{"text": "button1", "callback_data": "test_data"}]
    response = await telegram_api_client.send_inline_keyboard(
        chat_id=123, buttons=buttons
    )
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_send_inline_keyboard_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test sending of an inline keyboard with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    buttons = [{"text": "button1", "callback_data": "test_data"}]
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.send_inline_keyboard(chat_id=123, buttons=buttons)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_remove_keyboard_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful removal of keyboard.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )

    response = await telegram_api_client.remove_keyboard(chat_id=123)
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_remove_keyboard_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test removal of keyboard with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.remove_keyboard(chat_id=123)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_media_group_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful sending of media group.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    media = [
        {"type": "photo", "media": "test_photo_url"},
        {"type": "video", "media": "test_video_url"},
    ]
    response = await telegram_api_client.send_media_group(chat_id=123, media=media)
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_send_media_group_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
     Test sending of media group with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    media = [
        {"type": "photo", "media": "test_photo_url"},
        {"type": "video", "media": "test_video_url"},
    ]
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.send_media_group(chat_id=123, media=media)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()
    
@pytest.mark.asyncio
async def test_get_chat_members_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful get chat members.
    """
    mock_httpx_client.get.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True, "result": []})
    )
    response = await telegram_api_client.get_chat_members(chat_id=123)
    assert response == {"ok": True, "result": []}
    mock_httpx_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_chat_members_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test get chat members with telegram api exception.
    """
    mock_httpx_client.get.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
        await telegram_api_client.get_chat_members(chat_id=123)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_ban_chat_member_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful ban chat member.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    response = await telegram_api_client.ban_chat_member(chat_id=123, user_id=456)
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_ban_chat_member_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test ban chat member with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.ban_chat_member(chat_id=123, user_id=456)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_unban_chat_member_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful unban chat member.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    response = await telegram_api_client.unban_chat_member(chat_id=123, user_id=456)
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_unban_chat_member_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test unban chat member with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.unban_chat_member(chat_id=123, user_id=456)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_set_chat_title_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful set chat title.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    response = await telegram_api_client.set_chat_title(chat_id=123, title="test title")
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_set_chat_title_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test set chat title with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
        await telegram_api_client.set_chat_title(chat_id=123, title="test title")
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_set_chat_description_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful set chat description.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    response = await telegram_api_client.set_chat_description(chat_id=123, description="test description")
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_set_chat_description_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test set chat description with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
       await telegram_api_client.set_chat_description(chat_id=123, description="test description")
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_pin_chat_message_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test successful pin chat message.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    response = await telegram_api_client.pin_chat_message(chat_id=123, message_id=456)
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_pin_chat_message_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test pin chat message with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.pin_chat_message(chat_id=123, message_id=456)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_unpin_chat_message_success(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
     Test successful unpin chat message.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=200, json=AsyncMock(return_value={"ok": True})
    )
    response = await telegram_api_client.unpin_chat_message(chat_id=123, message_id=456)
    assert response == {"ok": True}
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_unpin_chat_message_fail(
    telegram_api_client: TelegramAPI, mock_httpx_client: AsyncMock
):
    """
    Test unpin chat message with telegram api exception.
    """
    mock_httpx_client.post.return_value = AsyncMock(
        status_code=400, json=AsyncMock(return_value={"ok": False, "description": "Test error"})
    )
    with pytest.raises(TelegramAPIException) as exc_info:
         await telegram_api_client.unpin_chat_message(chat_id=123, message_id=456)
    assert "Test error" in str(exc_info.value)
    mock_httpx_client.post.assert_called_once()