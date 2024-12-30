import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional

from src.core.logic_manager.base import LogicManager, Block
from src.core.utils.exceptions import TelegramAPIException
from src.db.repositories import BlockRepository, BotRepository
from src.integrations import AuthService, get_telegram_client
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_execute_bot_logic_success():
    """Test execute bot logic successfully."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)

    test_bot = {
        "id": 1,
        "logic": {"start_block_id": 10, "connections": []},
         "token": "test_token",
         "library": "telegram_api"
    }
    test_block = {"id": 10, "type": "text_message", "content": {"text": "Hello"}}

    mock_bot_repository.get_by_id.return_value = test_bot
    mock_block_repository.get_by_id.return_value = test_block
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}


    logic_manager = LogicManager(
        block_repository=mock_block_repository,
        bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )

    await logic_manager.execute_bot_logic(bot_id=1, chat_id=123, user_message="test_message")
    mock_block_repository.get_by_id.assert_called()


@pytest.mark.asyncio
async def test_execute_bot_logic_bot_not_found():
    """Test execute bot logic when bot not found."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)
    mock_bot_repository.get_by_id.return_value = None

    logic_manager = LogicManager(
        block_repository=mock_block_repository,
        bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )

    with pytest.raises(HTTPException) as exc_info:
        await logic_manager.execute_bot_logic(bot_id=1, chat_id=123, user_message="test_message", user={})
    assert exc_info.value.status_code == 404
    assert "Bot or bot logic was not found" in exc_info.value.detail
    
    mock_bot_repository.get_by_id.assert_called_once_with(1)
    

@pytest.mark.asyncio
async def test_execute_bot_logic_no_start_block():
     """Test execute bot logic when start block not found."""
     mock_block_repository = AsyncMock(spec=BlockRepository)
     mock_bot_repository = AsyncMock(spec=BotRepository)
     mock_auth_service = AsyncMock(spec=AuthService)
     test_bot = {"id": 1, "logic": {}, "token": "test_token", "library": "telegram_api"}
     mock_bot_repository.get_by_id.return_value = test_bot
     mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}

     logic_manager = LogicManager(
         block_repository=mock_block_repository,
         bot_repository=mock_bot_repository,
         auth_service=mock_auth_service,
    )

     with pytest.raises(HTTPException) as exc_info:
         await logic_manager.execute_bot_logic(bot_id=1, chat_id=123, user_message="test_message", user={})
     assert exc_info.value.status_code == 404
     assert "Start block id not found for bot" in exc_info.value.detail
     mock_bot_repository.get_by_id.assert_called_once_with(1)
     
@pytest.mark.asyncio
async def test_execute_bot_logic_unauthorized():
    """Test execute bot logic with unauthorized user."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)
    test_bot = {
        "id": 1,
        "logic": {"start_block_id": 10},
          "token": "test_token",
        "library": "telegram_api"
    }
    mock_bot_repository.get_by_id.return_value = test_bot
    mock_auth_service.get_user_by_token.return_value = {"id": 1, "roles": ["user"]}


    logic_manager = LogicManager(
        block_repository=mock_block_repository,
        bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )
    with pytest.raises(HTTPException) as exc_info:
        await logic_manager.execute_bot_logic(bot_id=1, chat_id=123, user_message="test_message", user={"id": 1, "roles": ["user"]})
    assert exc_info.value.status_code == 403
    assert "Permission denied" in exc_info.value.detail

@pytest.mark.asyncio
async def test_process_block_unsupported_type():
     """Test process block with unsupported block type"""
     mock_block_repository = AsyncMock(spec=BlockRepository)
     mock_bot_repository = AsyncMock(spec=BotRepository)
     mock_auth_service = AsyncMock(spec=AuthService)
     logic_manager = LogicManager(
         block_repository=mock_block_repository,
         bot_repository=mock_bot_repository,
         auth_service=mock_auth_service,
    )
     test_block = Block(id=1, type="unsupported_block_type", content={})
     next_block_id = await logic_manager._process_block(
            block=test_block, chat_id=123, user_message="test_message", bot_logic={}, variables={}
        )
     assert next_block_id is None

@pytest.mark.asyncio
async def test_process_block_no_next_blocks():
    """Test process block with no next blocks."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)
    logic_manager = LogicManager(
        block_repository=mock_block_repository,
        bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )
    test_block = Block(id=1, type="send_text", content={"text": "test"})
    mock_block_repository.list_by_ids.return_value = []

    next_block_id = await logic_manager._process_block(
        block=test_block, chat_id=123, user_message="test_message", bot_logic={"connections": []}, variables={}
    )
    assert next_block_id is None
    mock_block_repository.list_by_ids.assert_not_called()

@pytest.mark.asyncio
async def test_process_block_with_next_block_success():
    """Test process block with next blocks."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)
   
    test_block = Block(id=1, type="send_text", content={"text": "test"})
    test_next_block = Block(id=2, type="text_message", content={"text": "test_next"})

    mock_block_repository.list_by_ids.return_value = [test_next_block]
    mock_block_repository.get_by_id.return_value = test_next_block

    logic_manager = LogicManager(
        block_repository=mock_block_repository,
        bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )
    
    next_block_id = await logic_manager._process_block(
         block=test_block, chat_id=123, user_message="test_message", bot_logic={"connections": [{"source_block_id":1, "target_block_id": 2}]}, variables={}
     )
    assert next_block_id is None
    mock_block_repository.list_by_ids.assert_called_once()

@pytest.mark.asyncio
async def test_safe_execute_http_exception():
    """Test safe execute with http exception."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)
    logic_manager = LogicManager(
         block_repository=mock_block_repository,
         bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )

    mock_handler = AsyncMock(side_effect=HTTPException(status_code=400, detail="Test exception"))
    test_block = Block(id=1, type="test_block", content={})
    with pytest.raises(HTTPException) as exc_info:
        await logic_manager._safe_execute(
            handler=mock_handler,
            content={},
            chat_id=123,
             user_message="test_message",
             bot_logic={},
            variables={},
             block=test_block
        )
    assert "Test exception" in exc_info.value.detail
    mock_handler.assert_called_once()
    

@pytest.mark.asyncio
async def test_safe_execute_unhandled_exception():
    """Test safe execute with unhandled exception."""
    mock_block_repository = AsyncMock(spec=BlockRepository)
    mock_bot_repository = AsyncMock(spec=BotRepository)
    mock_auth_service = AsyncMock(spec=AuthService)
    logic_manager = LogicManager(
         block_repository=mock_block_repository,
         bot_repository=mock_bot_repository,
        auth_service=mock_auth_service,
    )
    mock_handler = AsyncMock(side_effect=Exception("Test unhandled exception"))
    test_block = Block(id=1, type="test_block", content={})
    with pytest.raises(HTTPException) as exc_info:
         await logic_manager._safe_execute(
            handler=mock_handler,
            content={},
            chat_id=123,
             user_message="test_message",
             bot_logic={},
            variables={},
             block=test_block
         )
    assert "Internal server error" in str(exc_info.value.detail)
    mock_handler.assert_called_once()