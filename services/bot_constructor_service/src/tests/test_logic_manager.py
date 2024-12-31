import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager import LogicManager
from src.integrations.telegram import TelegramAPI
from src.core.logic_manager.base import Block
from typing import Dict, Any, List
from src.db import get_session
from sqlalchemy import text
from src.core.utils.exceptions import ObjectNotFoundException

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
async def create_test_connection(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test connection in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO connections (source_block_id, target_block_id)
            VALUES (:source_block_id, :target_block_id)
            RETURNING id, source_block_id, target_block_id, type;
            """
        )
        params = {"source_block_id": block_id, "target_block_id": block_id}
        result = await session.execute(query, params)
        await session.commit()
        connection = result.fetchone()
        return dict(connection._mapping)

@pytest.mark.asyncio
async def test_get_next_blocks_success(mock_telegram_api: AsyncMock, create_test_block: Dict[str, Any], create_test_connection: Dict[str, Any]):
    """
    Test successful get next blocks for block.
    """
    logic_manager = LogicManager()
    test_block =  Block(**create_test_block)
    test_connection = create_test_connection
    
    async with get_session() as session:
        query = text(
            """
            SELECT * FROM blocks WHERE id = :target_block_id
        """
        )
        params = {"target_block_id": test_connection["target_block_id"]}
        result = await session.execute(query, params)
        next_block = result.fetchone()
        
    next_blocks = await logic_manager._get_next_blocks(test_block.id, bot_logic={"start":test_block.id, "next_blocks": {str(test_block.id): [test_connection["target_block_id"]]}})
    assert len(next_blocks) == 1
    assert next_blocks[0].id == next_block["id"]
    assert next_blocks[0].type == next_block["type"]
    assert next_blocks[0].content == next_block["content"]


@pytest.mark.asyncio
async def test_get_next_blocks_not_found_block(
    mock_telegram_api: AsyncMock, create_test_block: Dict[str, Any], create_test_connection: Dict[str, Any]
):
    """
    Test get next blocks for block with not found block.
    """
    logic_manager = LogicManager()
    test_block =  Block(**create_test_block)
    
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await logic_manager._get_next_blocks(test_block.id, bot_logic={"start":test_block.id, "next_blocks": {str(test_block.id): [999]}})
    assert str(exc_info.value) == "Block not found"


@pytest.mark.asyncio
async def test_process_block_success(mock_telegram_api: AsyncMock, create_test_block: Dict[str, Any]):
    """
    Test successful process block.
    """
    logic_manager = LogicManager()
    test_block = Block(**create_test_block)
    
    next_block_id = await logic_manager.process_block(
        block=test_block, chat_id=123, variables={}, bot_logic={} , user_message=""
    )
    assert next_block_id is None

@pytest.mark.asyncio
async def test_process_block_not_found_handler(mock_telegram_api: AsyncMock, create_test_block: Dict[str, Any]):
    """
    Test process block with not found handler for block.
    """
    logic_manager = LogicManager()
    test_block = Block(**create_test_block)
    test_block.type = "test_type"
    
    next_block_id = await logic_manager.process_block(
       block=test_block, chat_id=123, variables={}, bot_logic={}, user_message=""
    )
    assert next_block_id is None

@pytest.mark.asyncio
async def test_process_bot_logic_success(mock_telegram_api: AsyncMock, create_test_block: Dict[str, Any], create_test_connection: Dict[str, Any]):
    """
    Test successful process bot logic.
    """
    logic_manager = LogicManager()
    test_block = Block(**create_test_block)
    test_connection = create_test_connection
    bot_logic = {
        "start": test_block.id,
        "next_blocks": {str(test_block.id): [test_connection["target_block_id"]]},
    }
    async with get_session() as session:
        query = text(
            """
            SELECT * FROM blocks WHERE id = :target_block_id
        """
        )
        params = {"target_block_id": test_connection["target_block_id"]}
        result = await session.execute(query, params)
        next_block = result.fetchone()
    
    next_block_id = await logic_manager.process_bot_logic(
       chat_id=123, variables={}, bot_logic=bot_logic, user_message="", start_block_id=test_block.id
    )
    assert next_block_id == next_block["id"]