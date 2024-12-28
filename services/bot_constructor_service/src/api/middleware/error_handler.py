from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.schemas import ErrorResponse
from src.config import settings
from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class ErrorHandlerMiddleware:
    """
    Middleware for handling exceptions and returning structured error responses.
    """

    async def __call__(self, request: Request, call_next):
        """
        Handles exceptions during request processing and returns a JSON response.
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            logging_client.warning(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(
                    detail=exc.detail, status_code=exc.status_code
                ).model_dump(),
            )
        except Exception as exc:
            logging_client.exception(f"Internal Server Error: {exc}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    detail="Internal server error", status_code=500
                ).model_dump(),
            )