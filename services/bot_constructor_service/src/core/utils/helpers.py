from functools import wraps
from loguru import logger
from fastapi import HTTPException
from typing import Any, Callable, TypeVar, ParamSpec
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