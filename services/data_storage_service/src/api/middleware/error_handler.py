# services/data_storage_service/src/api/middleware/error_handler.py

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from loguru import logger
from src.api.schemas import ErrorResponse, ValidationErrorResponse

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return structured error responses.
    """

    def __init__(self, dispatch: Callable):
        super().__init__(dispatch)

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            logger.error(f"Validation error: {exc.errors()}")
            return JSONResponse(
                status_code=422,
                content=ValidationErrorResponse(
                    message="Validation error", errors=exc.errors()
                ).model_dump()
            )
        except HTTPException as exc:
             logger.error(f"HTTP Exception: {exc.detail}")
             return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(message=exc.detail).model_dump(),
            )
        except Exception as exc:
            logger.exception(f"An unexpected error occurred: {exc}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    message=f"Internal server error: {str(exc)}"
                ).model_dump(),
            )