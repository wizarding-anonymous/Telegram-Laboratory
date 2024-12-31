import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import user_handlers
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
async def test_save_user_data_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful saving user data.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "data": {"test_key": "test_value"}}
    
    result = await user_handlers.save_user_data(
        mock_telegram_api, test_data
    )
    assert result is not None

@pytest.mark.asyncio
async def test_save_user_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test save user data with not found block.
    """
    block_id = 999
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "data": {"test_key": "test_value"}}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await user_handlers.save_user_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"

@pytest.mark.asyncio
async def test_retrieve_user_data_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful retrieve user data.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "key": "test_key"}
    async with get_session() as session:
          query = text(
             """
             INSERT INTO user_data (block_id, chat_id, user_id, data)
            VALUES (:block_id, :chat_id, :user_id, :data)
           """
        )
          params = {
             "block_id": block_id,
             "chat_id": chat_id,
            "user_id": user_id,
              "data": {"test_key": "test_value"}
        }
          await session.execute(query, params)
          await session.commit()
    
    result = await user_handlers.retrieve_user_data(mock_telegram_api, test_data)
    assert result == "test_value"

@pytest.mark.asyncio
async def test_retrieve_user_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test retrieve user data with not found block.
    """
    block_id = 999
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "key": "test_key"}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await user_handlers.retrieve_user_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"

@pytest.mark.asyncio
async def test_retrieve_user_data_not_found_key(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test retrieve user data with not found key.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "key": "not_found_key"}
    
    async with get_session() as session:
          query = text(
             """
             INSERT INTO user_data (block_id, chat_id, user_id, data)
            VALUES (:block_id, :chat_id, :user_id, :data)
           """
        )
          params = {
             "block_id": block_id,
             "chat_id": chat_id,
            "user_id": user_id,
              "data": {"test_key": "test_value"}
        }
          await session.execute(query, params)
          await session.commit()
        
    result = await user_handlers.retrieve_user_data(mock_telegram_api, test_data)
    assert result is None


@pytest.mark.asyncio
async def test_clear_user_data_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful clear user data.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id}
    
    async with get_session() as session:
        query = text(
             """
             INSERT INTO user_data (block_id, chat_id, user_id, data)
            VALUES (:block_id, :chat_id, :user_id, :data)
           """
        )
        params = {
             "block_id": block_id,
             "chat_id": chat_id,
            "user_id": user_id,
              "data": {"test_key": "test_value"}
        }
        await session.execute(query, params)
        await session.commit()
    
    result = await user_handlers.clear_user_data(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_clear_user_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test clear user data with not found block.
    """
    block_id = 999
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await user_handlers.clear_user_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"

@pytest.mark.asyncio
async def test_manage_session_success(
    mock_telegram_api: AsyncMock,
     create_test_block: Dict[str, Any]
):
    """
    Test successful manage user session.
    """
    block_id = create_test_block["id"]
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "action": "start"}
    result = await user_handlers.manage_session(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_manage_session_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test manage user session with not found block.
    """
    block_id = 999
    chat_id = 123
    user_id = 456
    test_data = {"block_id": block_id, "chat_id": chat_id, "user_id": user_id, "action": "start"}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await user_handlers.manage_session(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Block not found"