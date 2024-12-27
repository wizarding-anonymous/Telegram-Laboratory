# services\user_dashboard\src\api\middleware\validation_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi.requests import Request
from pydantic import ValidationError
import logging

logger = logging.getLogger("validation_middleware")

class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware для валидации входных данных запросов.
    Проверяет тело запроса на корректность и структурные ошибки.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            if request.method in {"POST", "PUT", "PATCH"}:
                await self._validate_request_body(request)
        except ValidationError as ve:
            logger.error(f"Validation error: {ve.json()}")
            return JSONResponse(
                content={"detail": "Validation error", "errors": ve.errors()},
                status_code=422,
            )
        except Exception as e:
            logger.error(f"Unexpected error in validation middleware: {str(e)}")
            return JSONResponse(
                content={"detail": "Internal server error during validation"},
                status_code=500,
            )

        response = await call_next(request)
        return response

    async def _validate_request_body(self, request: Request):
        """
        Проверяет тело запроса на соответствие JSON-формату.
        """
        try:
            await request.json()  # Проверяем, что тело запроса корректный JSON
        except Exception as e:
            logger.warning(f"Invalid JSON format: {str(e)}")
            raise ValidationError(
                model="JSON Validation", errors=[{"msg": "Invalid JSON format"}]
            )
