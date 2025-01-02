from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from loguru import logger

from src.api.schemas import ErrorResponse, common_schema
from src.core.utils.exceptions import ValidationException, ServiceDiscoveryException, DatabaseException, IntegrationException
import json

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return structured error responses.
    """

    def __init__(self, dispatch: Callable):
        super().__init__(dispatch)

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response: Response = await call_next(request)
            return response
        except RequestValidationError as exc:
            logger.error(f"Validation error: {exc.errors()}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=common_schema.ErrorResponse(
                    message="Validation error",
                    details=exc.errors()
                ).model_dump()
            )
        except HTTPException as exc:
            logger.error(f"HTTP Exception: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                 content=common_schema.ErrorResponse(message=exc.detail).model_dump(),
            )
        except ValidationException as exc:
            logger.error(f"Validation Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=common_schema.ErrorResponse(message=str(exc)).model_dump()
            )
        except ServiceDiscoveryException as exc:
            logger.error(f"Service Discovery Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=common_schema.ErrorResponse(message=str(exc)).model_dump()
            )
        except DatabaseException as exc:
            logger.error(f"Database Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=common_schema.ErrorResponse(message=str(exc)).model_dump()
            )
        except IntegrationException as exc:
            logger.error(f"Integration Error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=common_schema.ErrorResponse(message=str(exc)).model_dump()
            )
        except Exception as exc:
            logger.exception(f"An unexpected error occurred: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=common_schema.ErrorResponse(
                    message=f"Internal server error: {str(exc)}"
                ).model_dump()
            )