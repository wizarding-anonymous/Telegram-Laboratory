import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import db_handlers
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
async def create_test_db_block(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test db block in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO databases (block_id, connection_params, query)
            VALUES (:block_id, :connection_params, :query)
            RETURNING id, block_id, connection_params, query, created_at;
            """
        )
        params = {
            "block_id": block_id,
            "connection_params": {"db_uri": "test_uri"},
            "query": "test_query",
        }
        result = await session.execute(query, params)
        await session.commit()
        db_block = result.fetchone()
        return dict(db_block._mapping)


@pytest.mark.asyncio
async def test_db_connect_success(
    mock_telegram_api: AsyncMock, create_test_db_block: Dict[str, Any]
):
    """
    Test successful connection to db.
    """
    block_id = create_test_db_block["id"]
    test_data = {"block_id": block_id}
    result = await db_handlers.db_connect(mock_telegram_api, test_data)
    assert result is not None


@pytest.mark.asyncio
async def test_db_connect_not_found_block(
    mock_telegram_api: AsyncMock,
):
    """
    Test db connect with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await db_handlers.db_connect(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Database block not found"


@pytest.mark.asyncio
async def test_db_query_success(
    mock_telegram_api: AsyncMock, create_test_db_block: Dict[str, Any]
):
    """
    Test successful db query execution.
    """
    block_id = create_test_db_block["id"]
    test_data = {"block_id": block_id}
    result = await db_handlers.db_query(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_db_query_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test db query with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await db_handlers.db_query(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Database block not found"


@pytest.mark.asyncio
async def test_db_fetch_data_success(
    mock_telegram_api: AsyncMock, create_test_db_block: Dict[str, Any]
):
    """
    Test successful db fetch data.
    """
    block_id = create_test_db_block["id"]
    test_data = {"block_id": block_id}
    result = await db_handlers.db_fetch_data(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_db_fetch_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test db fetch data with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await db_handlers.db_fetch_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Database block not found"


@pytest.mark.asyncio
async def test_db_insert_data_success(
    mock_telegram_api: AsyncMock, create_test_db_block: Dict[str, Any]
):
    """
    Test successful db insert data.
    """
    block_id = create_test_db_block["id"]
    test_data = {"block_id": block_id}
    result = await db_handlers.db_insert_data(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_db_insert_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test db insert data with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await db_handlers.db_insert_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Database block not found"


@pytest.mark.asyncio
async def test_db_update_data_success(
    mock_telegram_api: AsyncMock, create_test_db_block: Dict[str, Any]
):
    """
    Test successful db update data.
    """
    block_id = create_test_db_block["id"]
    test_data = {"block_id": block_id}
    result = await db_handlers.db_update_data(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_db_update_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test db update data with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await db_handlers.db_update_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Database block not found"


@pytest.mark.asyncio
async def test_db_delete_data_success(
    mock_telegram_api: AsyncMock, create_test_db_block: Dict[str, Any]
):
    """
    Test successful db delete data.
    """
    block_id = create_test_db_block["id"]
    test_data = {"block_id": block_id}
    result = await db_handlers.db_delete_data(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_db_delete_data_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
    Test db delete data with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await db_handlers.db_delete_data(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Database block not found"