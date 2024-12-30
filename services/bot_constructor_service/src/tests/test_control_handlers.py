import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from src.core.logic_manager.handlers.control_handlers import ControlHandler
from src.core.utils.exceptions import TelegramAPIException
from src.core.logic_manager.base import Block


@pytest.mark.asyncio
async def test_handle_variable_block_define():
    """Test defining a variable."""
    handler = ControlHandler()
    variables = {}
    test_block = {
        "id": 1,
        "type": "variable",
        "content": {"action": "define", "name": "test_var", "value": "test_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "test_value"


@pytest.mark.asyncio
async def test_handle_variable_block_assign():
    """Test assigning a value to a variable."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
      "id": 1,
      "type": "variable",
        "content": {"action": "assign", "name": "test_var", "value": "new_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "new_value"


@pytest.mark.asyncio
async def test_handle_variable_block_retrieve():
    """Test retrieving a variable's value (no change to variables)."""
    handler = ControlHandler()
    variables = {"test_var": "existing_value"}
    test_block = {
     "id": 1,
     "type": "variable",
        "content": {"action": "retrieve", "name": "test_var"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "existing_value"

@pytest.mark.asyncio
async def test_handle_variable_block_update():
    """Test updating a variable's value."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
      "id": 1,
      "type": "variable",
        "content": {"action": "update", "name": "test_var", "value": "updated_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "updated_value"

@pytest.mark.asyncio
async def test_handle_variable_block_invalid_action():
    """Test with an invalid action."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
       "id": 1,
        "type": "variable",
        "content": {"action": "invalid_action", "name": "test_var"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "old_value"


@pytest.mark.asyncio
async def test_handle_if_condition_pass():
    """Test if condition passes."""
    handler = ControlHandler()
    variables = {"test_var": 5}
    test_block = {
        "id": 1,
        "type": "if_condition",
        "content": {"condition": "test_var > 3", "else_block_id": 2},
    }
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository
    from typing import Optional

    class MockBlockRepository(BlockRepository):
            async def get_by_id(self, block_id: int) -> Block:
               return Block(id=2, type="send_text", content={"content": "test"})
    mock_block_repository = MockBlockRepository()


    handler.block_repository = mock_block_repository

    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager

    next_block_id = await handler.handle_if_condition(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id == 2

@pytest.mark.asyncio
async def test_handle_if_condition_fail():
    """Test if condition fails."""
    handler = ControlHandler()
    variables = {"test_var": 1}
    test_block = {
        "id": 1,
        "type": "if_condition",
        "content": {"condition": "test_var > 3", "else_block_id": 2},
    }
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository
    from typing import Optional

    class MockBlockRepository(BlockRepository):
          async def get_by_id(self, block_id: int) -> Block:
                return Block(id=2, type="send_text", content={"content": "test"})
            
    mock_block_repository = MockBlockRepository()
    handler.block_repository = mock_block_repository
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]

    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager
    next_block_id = await handler.handle_if_condition(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id == 2

@pytest.mark.asyncio
async def test_handle_if_condition_error():
    """Test if condition fails with error."""
    handler = ControlHandler()
    variables = {"test_var": "test"}
    test_block = {
        "id": 1,
        "type": "if_condition",
        "content": {"condition": "test_var > 3", "else_block_id": 2},
    }
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository
    from typing import Optional
    class MockBlockRepository(BlockRepository):
          async def get_by_id(self, block_id: int) -> Block:
                return Block(id=2, type="send_text", content={"content": "test"})
            
    mock_block_repository = MockBlockRepository()
    handler.block_repository = mock_block_repository

    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]

    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager
    
    next_block_id = await handler.handle_if_condition(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id is None

@pytest.mark.asyncio
async def test_handle_wait_for_message():
    """Test wait for message block"""
    handler = ControlHandler()
    test_block = {
         "id": 1,
        "type": "wait_for_message",
        "content": {}
    }
    next_block_id = await handler.handle_wait_for_message(
        block=test_block, chat_id=123, variables={}
    )
    assert next_block_id is None