import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional

from src.core.logic_manager.handlers.media_group_handlers import MediaGroupHandler
from src.integrations.telegram.client import TelegramClient
from src.core.utils.exceptions import TelegramAPIException
from src.core.logic_manager.base import Block


@pytest.mark.asyncio
async def test_handle_media_group_success():
    """Test sending a media group successfully."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaGroupHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "media_group",
         "content": {"items": [{"type": "photo", "media": "test_photo", "caption": "test_caption"}]},
    }
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager

    next_block_id = await handler.handle_media_group(
        block=test_block, chat_id=123, variables={}, bot_logic={}
    )
    assert next_block_id == 2
    mock_client.send_media_group.assert_called_once()

@pytest.mark.asyncio
async def test_handle_media_group_no_items():
    """Test handling media group block with no items."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaGroupHandler(telegram_client=mock_client)
    test_block = {
        "id": 1,
        "type": "media_group",
        "content": {"items": []},
    }
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager

    next_block_id = await handler.handle_media_group(
      block=test_block, chat_id=123, variables={}, bot_logic={}
    )
    assert next_block_id is None
    mock_client.send_media_group.assert_not_called()


@pytest.mark.asyncio
async def test_handle_media_group_api_error():
    """Test handling media group with API error."""
    mock_client = AsyncMock(spec=TelegramClient)
    mock_client.send_media_group.side_effect = Exception("Telegram API error")
    test_token = 'test_token'
    telegram_client = TelegramClient(bot_token=test_token)

    handler = MediaGroupHandler(telegram_client=telegram_client)
    test_block = {
        "id": 1,
        "type": "media_group",
        "content": {"items": [{"type": "photo", "media": "test_photo", "caption": "test_caption"}]},
    }
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager


    with pytest.raises(TelegramAPIException) as exc_info:
        await handler.handle_media_group(
          block=test_block, chat_id=123, variables={}, bot_logic={}
        )
    assert "Telegram API error" in str(exc_info.value)
    mock_client.send_media_group.assert_called_once()
    
@pytest.mark.asyncio
async def test_handle_media_group_with_variables():
    """Test handling media group with variables."""
    mock_client = AsyncMock(spec=TelegramClient)
    handler = MediaGroupHandler(telegram_client=mock_client)
    test_block = {
         "id": 1,
        "type": "media_group",
         "content": {"items": [{"type": "photo", "media": "test_photo", "caption": "Hello, {{name}}!"}]},
    }
    variables = {"name": "Test"}
    
    from src.core.logic_manager import LogicManager
    class MockLogicManager(LogicManager):
            async def _get_next_blocks(self, block_id: int, bot_logic: Dict[str, Any]) -> List[Block]:
                return [Block(id=2, type="send_text", content={"content": "test"})]
    mock_logic_manager = MockLogicManager()
    handler.logic_manager = mock_logic_manager

    await handler.handle_media_group(
         block=test_block, chat_id=123, variables=variables, bot_logic={}
    )
    mock_client.send_media_group.assert_called_once()
    
    args, kwargs = mock_client.send_media_group.call_args
    media = kwargs["media"]
    assert media[0]["caption"] == "Hello, Test!"