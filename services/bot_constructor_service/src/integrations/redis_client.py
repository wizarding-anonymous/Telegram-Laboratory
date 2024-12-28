import redis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from loguru import logger
from src.config import settings
from typing import Optional, Any


class RedisClient:
    """
    A client for interacting with Redis.
    """

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._redis_client: Optional[Redis] = None
        logger.info("RedisClient initialized.")

    async def connect(self) -> None:
         """Connects to Redis."""
         try:
             self._redis_client = Redis.from_url(self.redis_url)
             await self._redis_client.ping()
             logger.info("Successfully connected to Redis.")
         except ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis_client = None
            raise

    async def close(self) -> None:
         """Closes the Redis connection."""
         if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis connection closed.")
            self._redis_client = None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Sets a key-value pair in Redis."""
        if not self._redis_client:
             logger.error("Redis connection is not established.")
             return False

        try:
            result = await self._redis_client.set(key, value, ex=ex)
            logger.debug(f"Set key: {key} with result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
         """Gets the value of a key from Redis."""
         if not self._redis_client:
             logger.error("Redis connection is not established.")
             return None
         try:
            value = await self._redis_client.get(key)
            logger.debug(f"Get key: {key}, value: {value}")
            return value
         except Exception as e:
             logger.error(f"Error getting key {key} from Redis: {e}")
             return None

    async def delete(self, key: str) -> bool:
        """Deletes a key from Redis."""
        if not self._redis_client:
            logger.error("Redis connection is not established.")
            return False
        try:
            result = await self._redis_client.delete(key)
            logger.debug(f"Delete key: {key} with result: {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Checks if a key exists in Redis."""
        if not self._redis_client:
            logger.error("Redis connection is not established.")
            return False
        try:
            result = await self._redis_client.exists(key)
            logger.debug(f"Key {key} exists: {result}")
            return bool(result)
        except Exception as e:
             logger.error(f"Error checking key {key} existence in Redis: {e}")
             return False
        
    async def clear_all(self) -> bool:
        """Clears all keys from redis db"""
        if not self._redis_client:
            logger.error("Redis connection is not established.")
            return False
        try:
            result = await self._redis_client.flushdb()
            logger.debug(f"Redis database cleared with result: {result}")
            return result
        except Exception as e:
             logger.error(f"Error clearing redis db: {e}")
             return False

redis_client = RedisClient()