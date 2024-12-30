import pytest
from unittest.mock import AsyncMock
from src.integrations.redis_client import RedisClient
from redis.exceptions import ConnectionError

@pytest.mark.asyncio
async def test_redis_connect_success():
    """Test Redis client connection successfully."""
    mock_redis = AsyncMock()
    redis_client = RedisClient(redis=mock_redis)
    await redis_client.connect()
    mock_redis.connect.assert_called_once()

@pytest.mark.asyncio
async def test_redis_connect_fail():
    """Test Redis client connection fail."""
    mock_redis = AsyncMock()
    mock_redis.connect.side_effect = ConnectionError("Test connection error")
    redis_client = RedisClient(redis=mock_redis)
    with pytest.raises(ConnectionError):
        await redis_client.connect()
    mock_redis.connect.assert_called_once()


@pytest.mark.asyncio
async def test_redis_set_get_delete():
    """Test set, get and delete operations on redis."""
    mock_redis = AsyncMock()
    redis_client = RedisClient(redis=mock_redis)
    await redis_client.connect()
    await redis_client.set("test_key", "test_value")
    mock_redis.set.assert_called_once_with("test_key", "test_value")

    mock_redis.get.return_value = "test_value"
    value = await redis_client.get("test_key")
    assert value == "test_value"
    mock_redis.get.assert_called_once_with("test_key")
    
    await redis_client.delete("test_key")
    mock_redis.delete.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_redis_exists():
    """Test redis exists method"""
    mock_redis = AsyncMock()
    redis_client = RedisClient(redis=mock_redis)
    await redis_client.connect()
    
    mock_redis.exists.return_value = 1
    exists = await redis_client.exists("test_key")
    assert exists == True
    mock_redis.exists.assert_called_once_with("test_key")

    mock_redis.exists.return_value = 0
    exists = await redis_client.exists("test_key")
    assert exists == False
    mock_redis.exists.assert_called_with("test_key")

@pytest.mark.asyncio
async def test_redis_setex():
    """Test redis setex method"""
    mock_redis = AsyncMock()
    redis_client = RedisClient(redis=mock_redis)
    await redis_client.connect()
    
    await redis_client.setex("test_key", 10, "test_value")
    mock_redis.setex.assert_called_once_with("test_key", 10, "test_value")

@pytest.mark.asyncio
async def test_redis_close():
    """Test redis client close method"""
    mock_redis = AsyncMock()
    redis_client = RedisClient(redis=mock_redis)
    await redis_client.connect()
    await redis_client.close()
    mock_redis.close.assert_called_once()