# services/auth_service/src/api/middleware/error_handler.py

import uuid
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from loguru import logger
from typing import Any, Dict
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_422_UNPROCESSABLE_ENTITY
)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware для централизованной обработки ошибок в приложении.
    """

    def __init__(self, app: ASGIApp):
        """
        Инициализация middleware обработки ошибок.

        Args:
            app (ASGIApp): ASGI приложение
        """
        super().__init__(app)
        self.error_handlers = {
            HTTP_400_BAD_REQUEST: self._handle_bad_request,
            HTTP_401_UNAUTHORIZED: self._handle_unauthorized,
            HTTP_403_FORBIDDEN: self._handle_forbidden,
            HTTP_404_NOT_FOUND: self._handle_not_found,
            HTTP_422_UNPROCESSABLE_ENTITY: self._handle_validation_error,
            HTTP_500_INTERNAL_SERVER_ERROR: self._handle_internal_error
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Any:
        """
        Обрабатывает запрос и перехватывает возможные исключения.

        Args:
            request (Request): Объект запроса FastAPI
            call_next (RequestResponseEndpoint): Следующий обработчик в цепочке middleware

        Returns:
            Any: Ответ от следующего обработчика или обработанная ошибка
        """
        try:
            # Логируем входящий запрос
            logger.debug(f"Processing request: {request.method} {request.url.path}")
            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            # Обрабатываем HTTP исключения
            logger.warning(
                f"HTTP Exception {http_exc.status_code}: {http_exc.detail} "
                f"for {request.method} {request.url.path}"
            )

            handler = self.error_handlers.get(
                http_exc.status_code,
                self._handle_default_http_error
            )
            return await handler(http_exc)

        except Exception as exc:
            # Обрабатываем неожиданные исключения
            error_id = uuid.uuid4()
            logger.exception(
                f"Unhandled exception [Error ID: {error_id}]: {request.method} {request.url.path} - {str(exc)}"
            )
            return await self._handle_internal_error(exc, error_id)

    def _create_error_response(
        self,
        status_code: int,
        detail: str,
        error_type: str = "Error",
        headers: Dict[str, str] = None
    ) -> JSONResponse:
        """
        Создает стандартизированный JSON-ответ с ошибкой.

        Args:
            status_code (int): HTTP код статуса
            detail (str): Детальное описание ошибки
            error_type (str): Тип ошибки
            headers (Dict[str, str], optional): Дополнительные заголовки

        Returns:
            JSONResponse: Стандартизированный ответ с ошибкой
        """
        content = {
            "error": error_type,
            "detail": detail,
            "status_code": status_code
        }
        return JSONResponse(
            status_code=status_code,
            content=content,
            headers=headers or {}
        )

    async def _handle_bad_request(self, exc: HTTPException) -> JSONResponse:
        """Обработчик ошибок 400 Bad Request."""
        return self._create_error_response(
            HTTP_400_BAD_REQUEST,
            exc.detail,
            "Bad Request"
        )

    async def _handle_unauthorized(self, exc: HTTPException) -> JSONResponse:
        """Обработчик ошибок 401 Unauthorized."""
        return self._create_error_response(
            HTTP_401_UNAUTHORIZED,
            exc.detail,
            "Unauthorized",
            {"WWW-Authenticate": "Bearer"}
        )

    async def _handle_forbidden(self, exc: HTTPException) -> JSONResponse:
        """Обработчик ошибок 403 Forbidden."""
        return self._create_error_response(
            HTTP_403_FORBIDDEN,
            exc.detail,
            "Forbidden"
        )

    async def _handle_not_found(self, exc: HTTPException) -> JSONResponse:
        """Обработчик ошибок 404 Not Found."""
        return self._create_error_response(
            HTTP_404_NOT_FOUND,
            exc.detail,
            "Not Found"
        )

    async def _handle_validation_error(self, exc: HTTPException) -> JSONResponse:
        """Обработчик ошибок 422 Validation Error."""
        return self._create_error_response(
            HTTP_422_UNPROCESSABLE_ENTITY,
            exc.detail,
            "Validation Error"
        )

    async def _handle_internal_error(self, exc: Exception, error_id: uuid.UUID) -> JSONResponse:
        """Обработчик ошибок 500 Internal Server Error."""
        # Логируем исключение с уникальным идентификатором ошибки
        logger.error(f"Internal Server Error [Error ID: {error_id}]: {str(exc)}", exc_info=True)
        return self._create_error_response(
            HTTP_500_INTERNAL_SERVER_ERROR,
            "An internal server error occurred. Please try again later.",
            "Internal Server Error",
            {"X-Error-ID": str(error_id)}
        )

    async def _handle_default_http_error(self, exc: HTTPException) -> JSONResponse:
        """Обработчик для остальных HTTP ошибок."""
        return self._create_error_response(
            exc.status_code,
            exc.detail,
            "HTTP Error",
            exc.headers
        )