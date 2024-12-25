# services\api_gateway\src\api\middleware\error_handler.py
from typing import Any, Dict, Optional, Type
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.exceptions import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationException,
    ServiceUnavailableError
)
from src.core.logger import get_logger

logger = get_logger(__name__)

class ErrorHandler:
    """
    Централизованный обработчик ошибок для API Gateway.
    Преобразует различные типы исключений в соответствующие HTTP-ответы.
    """
    
    def __init__(self) -> None:
        # Маппинг исключений на HTTP-статусы
        self.status_code_map: Dict[Type[Exception], int] = {
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            NotFoundError: status.HTTP_404_NOT_FOUND,
            ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            RequestValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE
        }

    async def __call__(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Основной метод обработки исключений.
        
        Args:
            request: FastAPI Request объект
            exc: Перехваченное исключение

        Returns:
            JSONResponse с информацией об ошибке
        """
        return await self.handle_exception(request, exc)

    async def handle_exception(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Обработка различных типов исключений и формирование ответа.

        Args:
            request: FastAPI Request объект
            exc: Перехваченное исключение

        Returns:
            JSONResponse с деталями ошибки
        """
        # Логируем информацию о запросе и ошибке
        logger.error(
            f"Error processing request: {request.method} {request.url}",
            exc_info=exc
        )

        if isinstance(exc, StarletteHTTPException):
            return await self._handle_http_exception(exc)

        if isinstance(exc, RequestValidationError):
            return await self._handle_validation_error(exc)

        if isinstance(exc, ApplicationError):
            return await self._handle_application_error(exc)

        # Для необработанных исключений возвращаем 500 Internal Server Error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self._create_error_response(
                "Internal server error",
                code="INTERNAL_ERROR",
                details=str(exc) if str(exc) else None
            )
        )

    async def _handle_http_exception(
        self,
        exc: StarletteHTTPException
    ) -> JSONResponse:
        """Обработка HTTP исключений."""
        return JSONResponse(
            status_code=exc.status_code,
            content=self._create_error_response(
                exc.detail,
                code=f"HTTP_{exc.status_code}"
            )
        )

    async def _handle_validation_error(
        self,
        exc: RequestValidationError
    ) -> JSONResponse:
        """Обработка ошибок валидации."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=self._create_error_response(
                "Validation error",
                code="VALIDATION_ERROR",
                details=[
                    {
                        "loc": err["loc"],
                        "msg": err["msg"],
                        "type": err["type"]
                    }
                    for err in exc.errors()
                ]
            )
        )

    async def _handle_application_error(
        self,
        exc: ApplicationError
    ) -> JSONResponse:
        """Обработка пользовательских исключений приложения."""
        status_code = self.status_code_map.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        return JSONResponse(
            status_code=status_code,
            content=self._create_error_response(
                str(exc),
                code=exc.code if hasattr(exc, 'code') else "APPLICATION_ERROR",
                details=exc.details if hasattr(exc, 'details') else None
            )
        )

    def _create_error_response(
        self,
        message: str,
        code: str,
        details: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Создание структурированного ответа об ошибке.

        Args:
            message: Сообщение об ошибке
            code: Код ошибки
            details: Дополнительные детали ошибки

        Returns:
            Словарь с информацией об ошибке
        """
        response = {
            "error": {
                "message": message,
                "code": code
            }
        }
        
        if details is not None:
            response["error"]["details"] = details
            
        return response


def setup_error_handler(app):
    """
    Регистрация обработчиков ошибок в приложении FastAPI.

    Args:
        app: Экземпляр FastAPI приложения
    """
    error_handler = ErrorHandler()
    
    app.add_exception_handler(Exception, error_handler)
    app.add_exception_handler(StarletteHTTPException, error_handler)
    app.add_exception_handler(RequestValidationError, error_handler)
    app.add_exception_handler(ValidationError, error_handler)