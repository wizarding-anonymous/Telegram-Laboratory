import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from typing import Dict, Any, Optional, List
from src.core.logic_manager.handlers.error_handlers import ErrorHandler
from src.core.utils.exceptions import TelegramAPIException, ObjectNotFoundException
from src.core.logic_manager.base import Block
from src.db.repositories import BlockRepository

@pytest.fixture
def mock_block_repository() -> AsyncMock:
    """
    Fixture to create a mock BlockRepository.
    """
    mock = AsyncMock(spec=BlockRepository)
    return mock

@pytest.mark.asyncio
async def test_handle_try_catch_success(mock_block_repository: AsyncMock):
    """Test try catch block success."""
    handler = ErrorHandler()
    test_block = {
          "id": 1,
        "type": "try_catch",
        "content": {},
    }
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager
    
    next_block_id = await handler.handle_try_catch(
        block=test_block, chat_id=123, variables={}, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id == 2

@pytest.mark.asyncio
async def test_handle_try_catch_exception(mock_block_repository: AsyncMock):
    """Test try catch block with exception."""
    handler = ErrorHandler()
    test_block = {
         "id": 1,
        "type": "try_catch",
        "content": {"catch_block_id": 2},
    }
    
    mock_block_repository.get_by_id.return_value = Block(id=2, type="send_text", content={"content": "test"})
        
    handler.block_repository = mock_block_repository
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
        async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                raise Exception("Test Exception")
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager
    
    next_block_id = await handler.handle_try_catch(
         block=test_block, chat_id=123, variables={}, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id == 2
    mock_block_repository.get_by_id.assert_called_once_with(2)


@pytest.mark.asyncio
async def test_handle_raise_error_block_success():
    """Test raise error block successfully."""
    handler = ErrorHandler()
    test_block = {
        "id": 1,
        "type": "raise_error",
        "content": {"message": "Test error message"},
    }
    variables = {"test_var": "test_value"}
    with pytest.raises(HTTPException) as exc_info:
         await handler.handle_raise_error(
             block=test_block, chat_id=123, variables=variables, user_message="", bot_logic={}
        )
    assert "Test error message" in exc_info.value.detail
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_handle_raise_error_block_no_message():
    """Test raise error block with no message."""
    handler = ErrorHandler()
    test_block = {
        "id": 1,
        "type": "raise_error",
        "content": {},
    }
    with pytest.raises(HTTPException) as exc_info:
         await handler.handle_raise_error(
             block=test_block, chat_id=123, variables={}, user_message="", bot_logic={}
        )
    assert "Error message was not provided" in str(exc_info.value.detail)
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_handle_exception_success(mock_block_repository: AsyncMock):
    """Test handle exception block successfully."""
    handler = ErrorHandler()
    test_block = {
        "id": 1,
        "type": "handle_exception",
        "content": {"exception_block_id": 2},
    }
    
    mock_block_repository.get_by_id.return_value = Block(id=2, type="send_text", content={"content": "test"})
    handler.block_repository = mock_block_repository
    
    next_block_id = await handler.handle_handle_exception(
       block=test_block, chat_id=123, variables={}, bot_logic={}, user_message=""
    )
    assert next_block_id == 2
    mock_block_repository.get_by_id.assert_called_once_with(2)


@pytest.mark.asyncio
async def test_handle_exception_no_block_defined(mock_block_repository: AsyncMock):
    """Test handle exception with no exception block defined."""
    handler = ErrorHandler()
    test_block = {
         "id": 1,
        "type": "handle_exception",
        "content": {},
    }
    
    
    handler.block_repository = mock_block_repository
    next_block_id = await handler.handle_handle_exception(
      block=test_block, chat_id=123, variables={}, bot_logic={}, user_message=""
    )
    assert next_block_id is None
    mock_block_repository.get_by_id.assert_not_called()

@pytest.mark.asyncio
async def test_handle_exception_block_not_found(mock_block_repository: AsyncMock):
    """Test handle exception block when exception block id is not found."""
    handler = ErrorHandler()
    test_block = {
        "id": 1,
        "type": "handle_exception",
        "content": {"exception_block_id": 2},
    }
    
    mock_block_repository.get_by_id.return_value = None
    handler.block_repository = mock_block_repository
    next_block_id = await handler.handle_handle_exception(
        block=test_block, chat_id=123, variables={}, bot_logic={}, user_message=""
    )
    assert next_block_id is None
    mock_block_repository.get_by_id.assert_called_once_with(2)

@pytest.mark.asyncio
async def test_handle_telegram_api_exception():
    """Test handle telegram api exception."""
    handler = ErrorHandler()
    test_block = {
         "id": 1,
        "type": "test_block",
        "content": {},
    }
    with pytest.raises(TelegramAPIException) as exc_info:
       await handler.handle_telegram_api_exception(
          block=test_block, chat_id=123, variables={}, bot_logic={}, user_message="", exception=Exception("Telegram Error")
        )
    assert "Telegram Error" in str(exc_info.value)
    
@pytest.mark.asyncio
async def test_handle_object_not_found_exception():
    """Test handle object not found exception."""
    handler = ErrorHandler()
    test_block = {
         "id": 1,
        "type": "test_block",
        "content": {},
    }
    with pytest.raises(ObjectNotFoundException) as exc_info:
       await handler.handle_object_not_found_exception(
          block=test_block, chat_id=123, variables={}, bot_logic={}, user_message="", exception=ObjectNotFoundException("Test Object Not Found")
        )
    assert "Test Object Not Found" in str(exc_info.value)