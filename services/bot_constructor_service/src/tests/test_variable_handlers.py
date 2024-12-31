import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import variable_handlers
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
async def create_test_variable(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test variable in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO variables (block_id, name, value)
            VALUES (:block_id, :name, :value)
            RETURNING id, block_id, name, value, created_at;
            """
        )
        params = {
             "block_id": block_id,
            "name": "test_var",
            "value": "test_value"
        }
        result = await session.execute(query, params)
        await session.commit()
        variable = result.fetchone()
        return dict(variable._mapping)

@pytest.mark.asyncio
async def test_define_variable_success(
    mock_telegram_api: AsyncMock,
    create_test_block: Dict[str, Any]
):
    """
    Test successful defining a variable.
    """
    block_id = create_test_block["id"]
    test_data = {"block_id": block_id, "name": "test_var", "value": "test_value"}
    result = await variable_handlers.define_variable(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_define_variable_not_found_block(
    mock_telegram_api: AsyncMock
):
    """
     Test defining a variable with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id, "name": "test_var", "value": "test_value"}
    with pytest.raises(ObjectNotFoundException) as exc_info:
      await variable_handlers.define_variable(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Variable block not found"


@pytest.mark.asyncio
async def test_assign_value_success(
    mock_telegram_api: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful assign value to variable.
    """
    variable_id = create_test_variable["id"]
    block_id = create_test_variable["block_id"]
    test_data = {"block_id": block_id, "variable_id": variable_id, "value": "new_test_value"}
    result = await variable_handlers.assign_value(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_assign_value_not_found_variable(
    mock_telegram_api: AsyncMock
):
    """
    Test assign value to variable with not found variable.
    """
    variable_id = 999
    block_id = 1
    test_data = {"block_id": block_id, "variable_id": variable_id, "value": "new_test_value"}
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await variable_handlers.assign_value(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Variable not found"

@pytest.mark.asyncio
async def test_retrieve_value_success(
    mock_telegram_api: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful retrieve value.
    """
    variable_id = create_test_variable["id"]
    block_id = create_test_variable["block_id"]
    test_data = {"block_id": block_id, "variable_id": variable_id}
    result = await variable_handlers.retrieve_value(mock_telegram_api, test_data)
    assert result == "test_value"


@pytest.mark.asyncio
async def test_retrieve_value_not_found_variable(
    mock_telegram_api: AsyncMock
):
    """
    Test retrieve value with not found variable.
    """
    variable_id = 999
    block_id = 1
    test_data = {"block_id": block_id, "variable_id": variable_id}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await variable_handlers.retrieve_value(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Variable not found"


@pytest.mark.asyncio
async def test_update_value_success(
    mock_telegram_api: AsyncMock,
    create_test_variable: Dict[str, Any]
):
    """
    Test successful update value.
    """
    variable_id = create_test_variable["id"]
    block_id = create_test_variable["block_id"]
    test_data = {"block_id": block_id, "variable_id": variable_id, "value": "updated_test_value"}
    result = await variable_handlers.update_value(mock_telegram_api, test_data)
    assert result is not None

@pytest.mark.asyncio
async def test_update_value_not_found_variable(
    mock_telegram_api: AsyncMock
):
    """
    Test update value with not found variable.
    """
    variable_id = 999
    block_id = 1
    test_data = {"block_id": block_id, "variable_id": variable_id, "value": "updated_test_value"}
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await variable_handlers.update_value(mock_telegram_api, test_data)
    assert str(exc_info.value) == "Variable not found"