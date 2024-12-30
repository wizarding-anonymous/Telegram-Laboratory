import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any
import json
from src.core.logic_manager.handlers.user_handlers import UserHandler
from src.integrations.redis_client import redis_client


@pytest.mark.asyncio
async def test_handle_save_user_data_new_data():
    """Test saving new user data."""
    mock_redis = AsyncMock()
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
        "id": 1,
        "type": "save_user_data",
        "content": {"data": {"key1": "value1"}},
    }
    await handler.handle_save_user_data(
        block=test_block, chat_id=123, variables={}
    )
    mock_redis.set.assert_called_once_with(
        "user_data:123", '{"key1": "value1"}'
    )

@pytest.mark.asyncio
async def test_handle_save_user_data_update_data():
    """Test updating existing user data."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"key1": "old_value"}'
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
        "id": 1,
        "type": "save_user_data",
        "content": {"data": {"key2": "value2"}},
    }
    await handler.handle_save_user_data(
        block=test_block, chat_id=123, variables={}
    )
    mock_redis.set.assert_called_once_with(
        "user_data:123", '{"key1": "old_value", "key2": "value2"}'
    )


@pytest.mark.asyncio
async def test_handle_save_user_data_template_value():
    """Test saving user data using a template."""
    mock_redis = AsyncMock()
    handler = UserHandler()
    handler.redis_client = mock_redis
    variables = {"name": "TestUser"}
    test_block = {
         "id": 1,
        "type": "save_user_data",
        "content": {"data": "Hello, {{name}}!"},
    }
    await handler.handle_save_user_data(
        block=test_block, chat_id=123, variables=variables
    )
    mock_redis.set.assert_called_once_with(
        "user_data:123", json.dumps("Hello, TestUser!")
    )


@pytest.mark.asyncio
async def test_handle_retrieve_user_data_success():
    """Test retrieving user data successfully."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"key1": "value1", "key2": "value2"}'
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
         "id": 1,
        "type": "retrieve_user_data",
        "content": {"key": "key1"},
    }
    variables = {}
    retrieved_data = await handler.handle_retrieve_user_data(
         block=test_block, chat_id=123, variables=variables
    )
    assert retrieved_data == "value1"
    mock_redis.get.assert_called_once_with("user_data:123")


@pytest.mark.asyncio
async def test_handle_retrieve_user_data_all_data():
    """Test retrieving all user data successfully."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"key1": "value1", "key2": "value2"}'
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
        "id": 1,
        "type": "retrieve_user_data",
        "content": {},
    }
    variables = {}
    retrieved_data = await handler.handle_retrieve_user_data(
        block=test_block, chat_id=123, variables=variables
    )
    assert retrieved_data == {"key1": "value1", "key2": "value2"}
    mock_redis.get.assert_called_once_with("user_data:123")


@pytest.mark.asyncio
async def test_handle_retrieve_user_data_not_found():
    """Test retrieving user data when key is not found."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
        "id": 1,
        "type": "retrieve_user_data",
        "content": {"key": "key1"},
    }
    variables = {}
    retrieved_data = await handler.handle_retrieve_user_data(
        block=test_block, chat_id=123, variables=variables
    )
    assert retrieved_data is None
    mock_redis.get.assert_called_once_with("user_data:123")


@pytest.mark.asyncio
async def test_handle_clear_user_data_success():
    """Test clearing user data successfully."""
    mock_redis = AsyncMock()
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
         "id": 1,
        "type": "clear_user_data",
         "content": {},
    }
    await handler.handle_clear_user_data(
         block=test_block, chat_id=123, variables={}
    )
    mock_redis.delete.assert_called_once_with("user_data:123")

@pytest.mark.asyncio
async def test_handle_manage_session_new_data():
     """Test manage session new data."""
     mock_redis = AsyncMock()
     handler = UserHandler()
     handler.redis_client = mock_redis
     test_block = {
         "id": 1,
        "type": "manage_session",
        "content": {"session_data": {"session_key": "session_value"}},
    }
     await handler.handle_manage_session(
        block=test_block, chat_id=123, variables={}
    )
     mock_redis.set.assert_called_once_with(
         "session:123", '{"session_key": "session_value"}'
    )

@pytest.mark.asyncio
async def test_handle_manage_session_update_data():
    """Test manage session update data."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"session_key": "old_value"}'
    handler = UserHandler()
    handler.redis_client = mock_redis
    test_block = {
        "id": 1,
        "type": "manage_session",
        "content": {"session_data": {"session_key2": "new_value"}},
    }
    await handler.handle_manage_session(
       block=test_block, chat_id=123, variables={}
    )
    mock_redis.set.assert_called_once_with(
        "session:123", '{"session_key": "old_value", "session_key2": "new_value"}'
    )

@pytest.mark.asyncio
async def test_handle_manage_session_template_value():
    """Test manage session with template value."""
    mock_redis = AsyncMock()
    handler = UserHandler()
    handler.redis_client = mock_redis
    variables = {"test": "test_value"}
    test_block = {
        "id": 1,
        "type": "manage_session",
         "content": {"session_data": "Session {{test}}"},
    }
    await handler.handle_manage_session(
        block=test_block, chat_id=123, variables=variables
    )
    mock_redis.set.assert_called_once_with(
       "session:123", json.dumps("Session test_value")
    )