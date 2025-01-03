from functools import wraps
from loguru import logger
from fastapi import HTTPException
from typing import Any, Callable, TypeVar, ParamSpec
import json
from inspect import isawaitable

P = ParamSpec("P")
R = TypeVar("R")


def handle_exceptions(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to handle exceptions for async and sync functions.

    Args:
        func: The function to decorate.

    Returns:
        Decorated function with exception handling.
    """
    @wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            result = func(*args, **kwargs)
            if isawaitable(result):
                 return await result
            return result
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            raise
        except Exception as exc:
            logger.exception("An unexpected error occurred")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(exc)}"
            ) from exc

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
      try:
            return func(*args, **kwargs)
      except HTTPException as exc:
           logger.error(f"HTTP Exception: {exc.detail}")
           raise
      except Exception as exc:
          logger.exception("An unexpected error occurred")
          raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(exc)}"
            ) from exc


    if isawaitable(func):
        return async_wrapper
    else:
        return sync_wrapper


def log_request_response(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to log requests and responses for sync and async functions.
    """
    @wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            logger.debug(f"Request to: {func.__name__}, args: {args}, kwargs: {kwargs}")
            result = func(*args, **kwargs)
            if isawaitable(result):
               response = await result
            else:
               response = result
            logger.debug(f"Response from {func.__name__}: {response}")
            return response
        except Exception:
             logger.exception(f"Error during request/response in {func.__name__}")
             raise

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
           logger.debug(f"Request to: {func.__name__}, args: {args}, kwargs: {kwargs}")
           response = func(*args, **kwargs)
           logger.debug(f"Response from {func.__name__}: {response}")
           return response
        except Exception:
            logger.exception(f"Error during request/response in {func.__name__}")
            raise
    if isawaitable(func):
        return async_wrapper
    else:
       return sync_wrapper

def validate_data(schema: Any):
    """
    Decorator to validate request data using a Pydantic schema for sync and async functions.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
           try:
               if 'request' in kwargs:
                   request_data = kwargs['request']
                   schema.parse_obj(request_data)
               result = func(*args, **kwargs)
               if isawaitable(result):
                 return await result
               return result
           except Exception as exc:
              logger.error(f"Data validation failed in {func.__name__}: {str(exc)}")
              raise HTTPException(status_code=400, detail=f"Invalid input data: {str(exc)}")

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
               if 'request' in kwargs:
                   request_data = kwargs['request']
                   schema.parse_obj(request_data)
               return func(*args, **kwargs)
            except Exception as exc:
               logger.error(f"Data validation failed in {func.__name__}: {str(exc)}")
               raise HTTPException(status_code=400, detail=f"Invalid input data: {str(exc)}")
        if isawaitable(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator