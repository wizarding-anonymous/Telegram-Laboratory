# src/api/middleware/__init__.py

# Импорт мидлваров для аутентификации и обработки ошибок
from .auth import AuthMiddleware
from .error_handler import ErrorHandlerMiddleware

# Экспорт мидлваров для удобства импорта в другие части проекта
__all__ = ["AuthMiddleware", "ErrorHandlerMiddleware"]
