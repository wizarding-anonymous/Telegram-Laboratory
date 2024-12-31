import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import flow_handlers
from src.integrations.telegram import TelegramAPI
from src.core.utils.exceptions import ObjectNotFoundException
from typing import Dict, Any, List
from src.core.logic_manager.base import Block
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
async def create_test_flow(create_test_block) -> Dict[str, Any]:
    """
    Fixture to create a test flow in the database.
    """
    block_id = create_test_block["id"]
    async with get_session() as session:
        query = text(
            """
            INSERT INTO flows (block_id, logic)
            VALUES (:block_id, :logic)
            RETURNING id, block_id, logic, created_at;
            """
        )
        params = {
            "block_id": block_id,
            "logic": {"start": block_id, "next_blocks": {str(block_id): [block_id]}},
        }
        result = await session.execute(query, params)
        await session.commit()
        flow = result.fetchone()
        return dict(flow._mapping)


@pytest.mark.asyncio
async def test_process_flow_chart_success(
    mock_telegram_api: AsyncMock,
    create_test_flow: Dict[str, Any],
    create_test_block: Dict[str, Any]
):
    """
    Test successful processing of a flow chart.
    """
    flow_id = create_test_flow["id"]
    start_block_id = create_test_block["id"]
    
    test_data = {
        "flow_id": flow_id,
        "chat_id": 123,
        "variables": {},
    }
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
         async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
            return [Block(id=start_block_id, type="message", content={"text": "Test message"})]
    mock_logic_manager = MockLogicManager()
    
    result = await flow_handlers.process_flow_chart(
       mock_telegram_api, test_data, mock_logic_manager
    )
    assert result is not None
    mock_telegram_api.send_message.assert_called_once()
    mock_telegram_api.send_message.assert_called_with(chat_id=123, text="Test message")


@pytest.mark.asyncio
async def test_process_flow_chart_not_found_flow(
    mock_telegram_api: AsyncMock,
):
    """
    Test processing flow chart with not found flow.
    """
    flow_id = 999
    test_data = {
        "flow_id": flow_id,
        "chat_id": 123,
         "variables": {},
    }
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
         async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
            return []
    mock_logic_manager = MockLogicManager()
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await flow_handlers.process_flow_chart(
             mock_telegram_api, test_data, mock_logic_manager
        )
    assert str(exc_info.value) == "Flow chart not found"
    mock_telegram_api.send_message.assert_not_called()