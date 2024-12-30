import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, Response
from fastapi import HTTPException

from src.core.logic_manager.handlers.api_handlers import ApiRequestHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException


@pytest.mark.asyncio
async def test_handle_api_request_success():
    """Test successful API request."""
    mock_client = AsyncMock(spec=AsyncClient)
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 200
    mock_response.text = '{"key": "value"}'
    mock_client.request.return_value = mock_response

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    api_handler = ApiRequestHandler(telegram_client=telegram_client)
    test_block = {
      "id": 1,
      "type": "api_request",
      "content": {
        "url": "https://example.com/api",
        "method": "GET",
         "response_block_id": 2,
        "headers": {"Content-Type": "application/json"},
        "params": {"param1": "value1"},
         "body": {"key": "test_value"}
      }
    }

    variables = {"variable_test": "test_var"}
    
    block_logic = {
        "connections": [{"source_block_id": 1, "target_block_id": 2}]
    }
    
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository

    class MockBlockRepository(BlockRepository):
        async def get_by_id(self, block_id: int) -> Block:
                return Block(id=2, type="send_text", content={"content": "test"})
            
        async def list_by_ids(self, block_ids: List[int]) -> List[Block]:
               return [Block(id=2, type="send_text", content={"content": "test"})]

        async def get_bot_by_block_id(self, block_id: int) -> int:
            return 1
    
    mock_block_repository = MockBlockRepository()


    api_handler.block_repository = mock_block_repository

    from src.core.logic_manager import LogicManager

    class MockLogicManager(LogicManager):
            async def _process_block(self, block: Block, chat_id: int, user_message: str, bot_logic: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Optional[int]:
                return None
            
    mock_logic_manager = MockLogicManager()
    api_handler.logic_manager = mock_logic_manager

    next_block_id = await api_handler.handle_api_request(
        block=Block(**test_block),
        chat_id=123,
        user_message="test_message",
        bot_logic=block_logic,
         variables=variables
       
    )

    assert next_block_id is None
    mock_client.request.assert_called_once()



@pytest.mark.asyncio
async def test_handle_api_request_http_error():
    """Test API request with HTTP error."""
    mock_client = AsyncMock(spec=AsyncClient)
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 404
    mock_response.text = '{"description": "Not found"}'
    mock_client.request.side_effect = httpx.HTTPError(
        "Not Found", request=None, response=mock_response
    )

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    api_handler = ApiRequestHandler(telegram_client=telegram_client)
    
    test_block = {
        "id": 1,
       "type": "api_request",
        "content": {
            "url": "https://example.com/api",
            "method": "GET",
            "headers": {"Content-Type": "application/json"},
            "params": {"param1": "value1"},
         "body": {"key": "test_value"}
        }
    }
    variables = {"variable_test": "test_var"}
    
    block_logic = {
        "connections": [{"source_block_id": 1, "target_block_id": 2}]
    }
    
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository

    class MockBlockRepository(BlockRepository):
        async def get_by_id(self, block_id: int) -> Block:
                return Block(id=2, type="send_text", content={"content": "test"})
    
    mock_block_repository = MockBlockRepository()


    api_handler.block_repository = mock_block_repository
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _process_block(self, block: Block, chat_id: int, user_message: str, bot_logic: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Optional[int]:
                return None

    mock_logic_manager = MockLogicManager()
    api_handler.logic_manager = mock_logic_manager


    with pytest.raises(TelegramAPIException) as exc_info:
      await api_handler.handle_api_request(
        block=Block(**test_block),
            chat_id=123,
            user_message="test_message",
            bot_logic=block_logic,
            variables=variables,
        )
    assert "Telegram API Error: Not found" in str(exc_info.value)
    mock_client.request.assert_called_once()

@pytest.mark.asyncio
async def test_handle_api_request_unexpected_error():
    """Test API request with an unexpected error."""
    mock_client = AsyncMock(spec=AsyncClient)
    mock_client.request.side_effect = Exception("Unexpected error")
    
    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    api_handler = ApiRequestHandler(telegram_client=telegram_client)
    
    test_block = {
        "id": 1,
       "type": "api_request",
        "content": {
            "url": "https://example.com/api",
            "method": "GET",
            "headers": {"Content-Type": "application/json"},
            "params": {"param1": "value1"},
         "body": {"key": "test_value"}
        }
    }
    variables = {"variable_test": "test_var"}
    
    block_logic = {
        "connections": [{"source_block_id": 1, "target_block_id": 2}]
    }
    
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository

    class MockBlockRepository(BlockRepository):
        async def get_by_id(self, block_id: int) -> Block:
                return Block(id=2, type="send_text", content={"content": "test"})
    
    mock_block_repository = MockBlockRepository()


    api_handler.block_repository = mock_block_repository
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _process_block(self, block: Block, chat_id: int, user_message: str, bot_logic: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Optional[int]:
                return None
    mock_logic_manager = MockLogicManager()
    api_handler.logic_manager = mock_logic_manager


    with pytest.raises(TelegramAPIException) as exc_info:
       await api_handler.handle_api_request(
            block=Block(**test_block),
            chat_id=123,
            user_message="test_message",
            bot_logic=block_logic,
            variables=variables,
        )
    assert "Internal server error" in str(exc_info.value)
    mock_client.request.assert_called_once()


@pytest.mark.asyncio
async def test_handle_api_request_invalid_json():
    """Test API request with invalid json."""
    mock_client = AsyncMock(spec=AsyncClient)
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 200
    mock_response.text = 'invalid json'
    mock_client.request.return_value = mock_response

    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    api_handler = ApiRequestHandler(telegram_client=telegram_client)
    
    test_block = {
         "id": 1,
       "type": "api_request",
        "content": {
            "url": "https://example.com/api",
            "method": "GET",
            "headers": {"Content-Type": "application/json"},
            "params": {"param1": "value1"},
            "body": {"key": "test_value"}
        }
    }
    variables = {"variable_test": "test_var"}
    
    block_logic = {
        "connections": [{"source_block_id": 1, "target_block_id": 2}]
    }
    
    from src.core.logic_manager.base import Block
    from src.db.repositories import BlockRepository

    class MockBlockRepository(BlockRepository):
        async def get_by_id(self, block_id: int) -> Block:
                return Block(id=2, type="send_text", content={"content": "test"})

    mock_block_repository = MockBlockRepository()
    
    api_handler.block_repository = mock_block_repository

    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _process_block(self, block: Block, chat_id: int, user_message: str, bot_logic: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> Optional[int]:
                return None

    mock_logic_manager = MockLogicManager()
    api_handler.logic_manager = mock_logic_manager

    with pytest.raises(HTTPException) as exc_info:
        await api_handler.handle_api_request(
            block=Block(**test_block),
            chat_id=123,
            user_message="test_message",
            bot_logic=block_logic,
            variables=variables,
        )
    assert "Telegram API Error: Invalid response" in str(exc_info.value.detail)
    assert exc_info.value.status_code == 200
    mock_client.request.assert_called_once()