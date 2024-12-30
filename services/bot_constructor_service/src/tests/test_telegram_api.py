import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
import json
from src.core.utils.exceptions import TelegramAPIException
from src.integrations.telegram.telegram_api_client import TelegramAPI
from src.config import settings


@pytest.mark.asyncio
async def test_send_message_success():
    """Test sending a message successfully."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}
    mock_client.request.return_value = mock_response

    telegram_api = TelegramAPI(client=mock_client)
    response = await telegram_api.send_message(chat_id=123, text="test_message")
    assert response == {"ok": True, "result": {"message_id": 123}}
    mock_client.request.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_http_error():
    """Test sending a message with an HTTP error."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 400
    mock_response.text = '{"description": "Test error"}'
    mock_client.request.side_effect = httpx.HTTPError(
        "Test error", request=None, response=mock_response
    )
    telegram_api = TelegramAPI(client=mock_client)
    with pytest.raises(TelegramAPIException) as exc_info:
        await telegram_api.send_message(chat_id=123, text="test_message")
    assert "Telegram API Error: Test error" in str(exc_info.value)
    mock_client.request.assert_called_once()

@pytest.mark.asyncio
async def test_send_message_unexpected_error():
    """Test sending a message with an unexpected error."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request.side_effect = Exception("Unexpected error")

    telegram_api = TelegramAPI(client=mock_client)
    with pytest.raises(TelegramAPIException) as exc_info:
        await telegram_api.send_message(chat_id=123, text="test_message")
    assert "Internal server error" in str(exc_info.value)
    mock_client.request.assert_called_once()

@pytest.mark.asyncio
async def test_send_message_invalid_json():
    """Test send message with invalid json in response."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = "invalid json"
    mock_client.request.return_value = mock_response

    telegram_api = TelegramAPI(client=mock_client)

    with pytest.raises(HTTPException) as exc_info:
        await telegram_api.send_message(chat_id=123, text="test_message")
    assert "Telegram API Error: Invalid response" in exc_info.value.detail
    mock_client.request.assert_called_once()
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_check_connection_success():
    """Test successful connection check"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_client.get.return_value = mock_response

    telegram_api = TelegramAPI(client=mock_client, bot_token="test_token")
    result = await telegram_api.check_connection()
    assert result == True
    mock_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_check_connection_fail():
    """Test connection check fail"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 401
    mock_client.get.side_effect = httpx.HTTPError(
        "Unauthorized", request=None, response=mock_response
    )

    telegram_api = TelegramAPI(client=mock_client, bot_token="test_token")
    result = await telegram_api.check_connection()
    assert result == False
    mock_client.get.assert_called_once()