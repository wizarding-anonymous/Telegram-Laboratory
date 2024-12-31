import pytest
from unittest.mock import AsyncMock
from src.core.logic_manager.handlers import polling_handlers
from src.integrations.telegram import TelegramAPI
from src.core.utils.exceptions import ObjectNotFoundException
from typing import Dict, Any
from src.db import get_session
from sqlalchemy import text
from src.core.logic_manager.base import Block

@pytest.fixture
def mock_telegram_api() -> AsyncMock:
    """
    Fixture to create a mock TelegramAPI client.
    """
    mock = AsyncMock(spec=TelegramAPI)
    mock.send_message.return_value = {"ok": True}
    mock.start_polling.return_value = None
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
async def test_start_polling_success(
    mock_telegram_api: AsyncMock, create_test_block: Dict[str, Any]
):
    """
    Test successful start polling.
    """
    block_id = create_test_block["id"]
    test_data = {"block_id": block_id}
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    
    result = await polling_handlers.start_polling(mock_telegram_api, test_data, mock_logic_manager)
    assert result is not None
    mock_telegram_api.start_polling.assert_called_once()

@pytest.mark.asyncio
async def test_start_polling_not_found_block(
     mock_telegram_api: AsyncMock,
    
):
    """
    Test start polling with not found block.
    """
    block_id = 999
    test_data = {"block_id": block_id}
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return []
    mock_logic_manager = MockLogicManager()
    
    with pytest.raises(ObjectNotFoundException) as exc_info:
        await polling_handlers.start_polling(mock_telegram_api, test_data, mock_logic_manager)
    assert str(exc_info.value) == "Block not found"
    mock_telegram_api.start_polling.assert_not_called()