from typing import Any, Dict, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from loguru import logger

from src.api.schemas import ErrorResponse
from src.core.utils.exceptions import ValidationException, ServiceDiscoveryException, DatabaseException, IntegrationException
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return structured error responses.
    """
    def __init__(self, dispatch: Callable):
        super().__init__(dispatch)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Intercepts and handles exceptions during request processing.
        """
        try:
            response: Response = await call_next(request)
            return response
        except RequestValidationError as exc:
            logger.error(f"Validation error: {exc.errors()}")
            logging_client.error(f"Validation error: {exc.errors()}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=ErrorResponse(
                    detail="Validation error",
                ).model_dump()
            )
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            logging_client.error(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(detail=exc.detail).model_dump(),
            )
        except ValidationException as exc:
            logger.error(f"Validation Error: {exc}")
            logging_client.error(f"Validation Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(detail=str(exc)).model_dump()
            )
        except ServiceDiscoveryException as exc:
            logger.error(f"Service Discovery Error: {exc}")
            logging_client.error(f"Service Discovery Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(detail=str(exc)).model_dump()
            )
        except DatabaseException as exc:
            logger.error(f"Database Error: {exc}")
            logging_client.error(f"Database Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(detail=str(exc)).model_dump()
            )
        except IntegrationException as exc:
            logger.error(f"Integration Error: {exc}")
            logging_client.error(f"Integration Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(detail=str(exc)).model_dump()
            )
        except Exception as exc:
            logger.exception(f"An unexpected error occurred: {exc}")
            logging_client.exception(f"An unexpected error occurred: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    detail=f"Internal server error: {str(exc)}"
                ).model_dump()
            )