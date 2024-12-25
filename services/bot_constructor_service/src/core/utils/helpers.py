# services\bot_constructor_service\src\core\utils\helpers.py
from functools import wraps
from loguru import logger
from fastapi import HTTPException

def handle_exceptions(func):
    """
    Decorator to handle exceptions for async functions.

    Args:
        func: The async function to decorate.

    Returns:
        Decorated function with exception handling.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            raise
        except Exception as exc:
            logger.exception("An unexpected error occurred")
            raise HTTPException(status_code=500, detail="Internal server error") from exc

    return wrapper
