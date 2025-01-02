# services/data_storage_service/src/core/utils/helpers.py

from functools import wraps
from loguru import logger
from fastapi import HTTPException
from typing import Any, Callable, TypeVar, ParamSpec
from datetime import datetime
import json

P = ParamSpec("P")
R = TypeVar("R")


def handle_exceptions(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to handle exceptions for async functions.

    Args:
        func: The async function to decorate.

    Returns:
        Decorated function with exception handling.
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            raise
        except Exception as exc:
            logger.exception("An unexpected error occurred")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(exc)}"
            ) from exc

    return wrapper


def generate_random_string(length: int = 10) -> str:
    """
    Generates a random string of specified length.
    """
    import uuid
    return str(uuid.uuid4())[:length]


def format_datetime(date_time: datetime) -> str:
    """
    Formats a datetime object into a string.
    """
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


async def check_migrations_status() -> bool:
    """
    Placeholder for checking migrations status.
    Will be implemented in future versions.
    """
    # Тут будет логика проверки миграций
    return True