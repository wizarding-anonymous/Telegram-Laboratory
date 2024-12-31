import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import message_handlers
from src.integrations.telegram import TelegramAPI
from src.core.utils.exceptions import ObjectNotFoundException
from typing import Dict, Any
from src.db import get_session
from sqlalchemy import text

@pytest.fixture
def mock_telegram_api() -> AsyncMock:
    """
    Fixture to create a mock TelegramAPI client.
    """
    mock = AsyncMock(spec=TelegramAPI)
    mock.send_message.return_value = {"ok": True}
    return mock

@pytest.fixture
async def create_test_bot() -> Dict[str, Any]:
    """
    Fixture to create a test bot in the database.
    """
    async with get_session() as session:
        query = text(
            """
            INSERT INTO bots (user_id, name)
            VALUES (:user_id, :name)
            RETURNING id, user_id, name, created_at;
        """
        )
        params = {"user_id": 1, "name": "Test Bot"}
        result = await session.execute(query, params)
        await session.commit()
        bot = result.fetchone()
        return dict(bot._mapping)


@pytest.fixture
async def create_test_block(create_test_bot) -> Dict[str, Any]:
    """
    Fixture to create a test block in the database.
    """
    bot_id = create_test_bot["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO blocks (bot_id, type, content)
            VALUES (:bot_id, :type, :content)
            RETURNING id, bot_id, type, content, created_at;
        """
        )
        params = {"bot_id": bot_id, "type": "message", "content": {"text": "Test message"}}
        result = await session.execute(query, params)
        await session.commit()
        block = result.fetchone()
        return dict(block._mapping)

@pytest.mark.asyncio
async def test_send_text_message_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful sending of a text message.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    result = await message_handlers.send_text_message(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.send_message.assert_called_once()
    mock_telegram_api.send_message.assert_called_with(chat_id=chat_id, text="Test message")

@pytest.mark.asyncio
async def test_send_text_message_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test send text message with not found block.
    """
    block_id = 999
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await message_handlers.send_text_message(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Message block not found"
    mock_telegram_api.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_text_message_with_template_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful sending of a text message with a template.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    test_data = {"block_id": block_id, "chat_id": chat_id, "template_context": {"test_var": "test_value_from_user"}}
    
    async with get_session() as session:
        query = text(
             """
             UPDATE blocks
            SET content = :content
            WHERE id = :block_id
           """
        )
        params = {
             "block_id": block_id,
             "content": {"text": "Test message with var: {{ test_var }}"}
        }
        await session.execute(query, params)
        await session.commit()
        
    result = await message_handlers.send_text_message(mock_telegram_api, test_data)
    assert result is not None
    mock_telegram_api.send_message.assert_called_once()
    mock_telegram_api.send_message.assert_called_with(chat_id=chat_id, text="Test message with var: test_value_from_user")