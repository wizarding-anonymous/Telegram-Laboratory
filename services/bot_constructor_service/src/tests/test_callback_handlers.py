import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import callback_handlers
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

@pytest.fixture
async def create_test_callback(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test callback in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
         query = text(
            """
            INSERT INTO callbacks (block_id, data)
            VALUES (:block_id, :data)
            RETURNING id, block_id, data, created_at;
            """
        )
         params = {"block_id": block_id, "data": "test_callback_data"}
         result = await session.execute(query, params)
         await session.commit()
         callback = result.fetchone()
         return dict(callback._mapping)


@pytest.mark.asyncio
async def test_process_callback_query_success(
    mock_telegram_api: AsyncMock,
    create_test_callback: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful processing of a callback query.
    """
    callback_id = create_test_callback["id"]
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    
    test_data = {
        "callback_id": callback_id,
        "chat_id": chat_id,
        "user_id": user_id,
        "data": "test_callback_data"
    }
    
    result = await callback_handlers.process_callback_query(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.send_message.assert_called_once()
    mock_telegram_api.send_message.assert_called_with(chat_id=chat_id, text="Test message")


@pytest.mark.asyncio
async def test_process_callback_query_not_found(
    mock_telegram_api: AsyncMock
):
    """
    Test processing callback query when callback not found.
    """
    callback_id = 999
    chat_id = 123
    user_id = 456
    test_data = {
        "callback_id": callback_id,
        "chat_id": chat_id,
        "user_id": user_id,
        "data": "test_callback_data"
    }
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await callback_handlers.process_callback_query(
            mock_telegram_api, test_data
        )
    assert str(exc_info.value) == "Callback not found"
    mock_telegram_api.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_process_callback_query_with_template_success(
    mock_telegram_api: AsyncMock,
    create_test_callback: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful processing of a callback query with template.
    """
    callback_id = create_test_callback["id"]
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    
    test_data = {
        "callback_id": callback_id,
        "chat_id": chat_id,
        "user_id": user_id,
        "data": "test_callback_data",
         "template_context":  {"test_var": "test_value_from_user"}
    }
    
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
    
    
    result = await callback_handlers.process_callback_query(
        mock_telegram_api, test_data
    )
    assert result is not None
    mock_telegram_api.send_message.assert_called_once()
    mock_telegram_api.send_message.assert_called_with(chat_id=chat_id, text="Test message with var: test_value_from_user")