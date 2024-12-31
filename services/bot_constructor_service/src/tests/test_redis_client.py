import pytest
from unittest.mock import AsyncMock
from src.integrations.redis_client import redis_client
from redis.exceptions import ConnectionError
from src.config import settings


@pytest.fixture
def mock_redis_client() -> AsyncMock:
    """
    Fixture to create a mock Redis client.
    """
    mock = AsyncMock(spec=redis_client)
    return mock


@pytest.mark.asyncio
async def test_redis_set_get_success(mock_redis_client: AsyncMock):
    """
    Test successful setting and getting value from Redis.
    """
    key = "test_key"
    value = "test_value"
    mock_redis_client.set.return_value = True
    mock_redis_client.get.return_value = value

    set_result = await redis_client.set(key, value)
    get_result = await redis_client.get(key)

    assert set_result is True
    assert get_result == value
    mock_redis_client.set.assert_called_once_with(key, value)
    mock_redis_client.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_redis_set_fail(mock_redis_client: AsyncMock):
    """
    Test setting value to redis with connection error.
    """
    key = "test_key"
    value = "test_value"
    mock_redis_client.set.side_effect = ConnectionError("Test Connection Error")

    with pytest.raises(ConnectionError) as exc_info:
        await redis_client.set(key, value)
    assert "Test Connection Error" in str(exc_info.value)
    mock_redis_client.set.assert_called_once_with(key, value)


@pytest.mark.asyncio
async def test_redis_get_fail(mock_redis_client: AsyncMock):
    """
    Test getting value from redis with connection error.
    """
    key = "test_key"
    mock_redis_client.get.side_effect = ConnectionError("Test Connection Error")
    with pytest.raises(ConnectionError) as exc_info:
        await redis_client.get(key)
    assert "Test Connection Error" in str(exc_info.value)
    mock_redis_client.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_redis_delete_success(mock_redis_client: AsyncMock):
    """
    Test successful deleting value from Redis.
    """
    key = "test_key"
    mock_redis_client.delete.return_value = 1
    delete_result = await redis_client.delete(key)
    assert delete_result == 1
    mock_redis_client.delete.assert_called_once_with(key)

@pytest.mark.asyncio
async def test_redis_delete_fail(mock_redis_client: AsyncMock):
    """
    Test deleting value from redis with connection error.
    """
    key = "test_key"
    mock_redis_client.delete.side_effect = ConnectionError("Test Connection Error")
    with pytest.raises(ConnectionError) as exc_info:
        await redis_client.delete(key)
    assert "Test Connection Error" in str(exc_info.value)
    mock_redis_client.delete.assert_called_once_with(key)