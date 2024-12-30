import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from src.core.logic_manager.handlers.db_handlers import DatabaseHandler
from src.db.database import get_session
from src.db.repositories import DatabaseRepository
from src.core.utils.exceptions import TelegramAPIException
from src.core.logic_manager.base import Block
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_handle_database_connect_success():
    """Test database connect block success."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock(spec=DatabaseRepository)
    mock_repo.create.return_value = None

    handler = DatabaseHandler(session=mock_session)
    handler.database_repository = mock_repo
    test_block = {
         "id": 1,
        "type": "database_connect",
        "content": {"db_uri": "postgresql://test_user:test_password@localhost:5432/test_db"},
    }
    await handler.handle_database_connect(
      block=test_block, chat_id=123, variables={}
    )
    mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_handle_database_connect_with_params():
     """Test database connect with connection params"""
     mock_session = AsyncMock(spec=AsyncSession)
     mock_repo = AsyncMock(spec=DatabaseRepository)
     mock_repo.create.return_value = None

     handler = DatabaseHandler(session=mock_session)
     handler.database_repository = mock_repo
     test_block = {
          "id": 1,
        "type": "database_connect",
        "content": {"connection_params": {"host": "test_host", "port": 5432}},
    }
     await handler.handle_database_connect(
        block=test_block, chat_id=123, variables={"test_var": "test_value"}
    )
     mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_handle_database_connect_no_params():
    """Test database connect without params"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock(spec=DatabaseRepository)
    mock_repo.create.return_value = None

    handler = DatabaseHandler(session=mock_session)
    handler.database_repository = mock_repo
    test_block = {
        "id": 1,
        "type": "database_connect",
        "content": {},
    }
    await handler.handle_database_connect(
        block=test_block, chat_id=123, variables={}
    )
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_handle_database_query_success():
    """Test database query successfuly."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock(spec=DatabaseRepository)
    mock_repo.execute_query.return_value = [{"test": "test"}]
    mock_repo.get_by_id.return_value = {"id": 1, "db_uri": "test_db_uri", "type": "database_connect"}
    
    handler = DatabaseHandler(session=mock_session)
    handler.database_repository = mock_repo
    test_block = {
       "id": 1,
        "type": "database_query",
        "content": {"query": "SELECT * FROM test_table;", "db_block_id": 1},
    }
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                 return [Block(id=2, type="send_text", content={"content": "test"})]

            async def _process_block(self, block: Block, chat_id: int, user_message: str, bot_logic: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Optional[int]:
                return None
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager
    
    next_block_id = await handler.handle_database_query(
        block=test_block, chat_id=123, variables={}, user_message="test_message", bot_logic={}
    )
    assert next_block_id is None
    mock_repo.execute_query.assert_called_once()

@pytest.mark.asyncio
async def test_handle_database_query_no_db_block():
    """Test database query with no database block id."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock(spec=DatabaseRepository)
    handler = DatabaseHandler(session=mock_session)
    handler.database_repository = mock_repo
    test_block = {
         "id": 1,
        "type": "database_query",
        "content": {"query": "SELECT * FROM test_table;"}
    }
    next_block_id = await handler.handle_database_query(
        block=test_block, chat_id=123, variables={}, user_message="test_message", bot_logic={}
    )
    assert next_block_id is None
    mock_repo.execute_query.assert_not_called()


@pytest.mark.asyncio
async def test_handle_database_query_api_error():
    """Test database query with api error."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock(spec=DatabaseRepository)
    mock_repo.execute_query.side_effect = Exception("Database error")
    mock_repo.get_by_id.return_value = {"id": 1, "db_uri": "test_db_uri", "type": "database_connect"}
    handler = DatabaseHandler(session=mock_session)
    handler.database_repository = mock_repo
    test_block = {
        "id": 1,
        "type": "database_query",
        "content": {"query": "SELECT * FROM test_table;", "db_block_id": 1},
    }
    with pytest.raises(Exception) as exc_info:
       await handler.handle_database_query(
            block=test_block, chat_id=123, variables={}, user_message="test_message", bot_logic={}
        )
    assert "Database query failed" in str(exc_info.value)
    mock_repo.execute_query.assert_called_once()