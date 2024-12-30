import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from src.core.logic_manager.handlers.flow_handlers import FlowHandler
from src.core.logic_manager.base import Block

@pytest.mark.asyncio
async def test_handle_if_condition_pass():
    """Test if condition passes."""
    handler = FlowHandler()
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
    handler = FlowHandler()
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
    handler = FlowHandler()
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
async def test_handle_loop_for_success():
    """Test loop for successfully."""
    handler = FlowHandler()
    variables = {}
    test_block = {
        "id": 1,
        "type": "loop",
         "content": {"loop_type": "for", "count": 2},
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
    next_block_id = await handler.handle_loop_block(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id == 2

@pytest.mark.asyncio
async def test_handle_loop_while_success():
    """Test loop while successfully."""
    handler = FlowHandler()
    variables = {"test_var": 5}
    test_block = {
         "id": 1,
        "type": "loop",
        "content": {"loop_type": "while", "condition": "test_var > 3"},
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
    
    next_block_id = await handler.handle_loop_block(
       block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message="5"
    )
    assert next_block_id == 2

@pytest.mark.asyncio
async def test_handle_loop_while_invalid_condition():
    """Test loop while with no condition."""
    handler = FlowHandler()
    variables = {"test_var": 1}
    test_block = {
        "id": 1,
        "type": "loop",
        "content": {"loop_type": "while",},
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
    next_block_id = await handler.handle_loop_block(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message="1"
    )
    assert next_block_id is None

@pytest.mark.asyncio
async def test_handle_switch_case_success():
    """Test switch case block successfully."""
    handler = FlowHandler()
    variables = {"test_var": "case1"}
    test_block = {
        "id": 1,
        "type": "switch_case",
        "content": {
            "switch_value": "test_var",
            "cases": [
                {"case_value": "case1", "target_block_id": 2},
                 {"case_value": "case2", "target_block_id": 3}
             ],
        },
    }
    next_block_id = await handler.handle_switch_case(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id == 2

@pytest.mark.asyncio
async def test_handle_switch_case_no_match():
    """Test switch case block with no match."""
    handler = FlowHandler()
    variables = {"test_var": "case3"}
    test_block = {
         "id": 1,
        "type": "switch_case",
        "content": {
            "switch_value": "test_var",
            "cases": [
                {"case_value": "case1", "target_block_id": 2},
                 {"case_value": "case2", "target_block_id": 3}
             ],
         },
    }
    next_block_id = await handler.handle_switch_case(
        block=test_block, chat_id=123, variables=variables, bot_logic={}, current_block_id=1, user_message=""
    )
    assert next_block_id is None