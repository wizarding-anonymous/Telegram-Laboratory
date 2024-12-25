# services\api_gateway\src\api\middleware\auth.py
from typing import Optional, List, Dict, Any
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import jwt
from datetime import datetime, timezone
import re

from src.db.database import get_session
from src.core.config import settings
from src.db.repositories.route_repository import RouteRepository
from src.integrations.auth_service import AuthService

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для аутентификации и авторизации запросов в API Gateway.
    Проверяет JWT токены и права доступа к маршрутам.
    """

    def __init__(
        self,
        app,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.JWT_ALGORITHM,
        public_paths: Optional[List[str]] = None
    ):
        """
        Инициализация middleware с необходимыми параметрами.

        Args:
            app: ASGI приложение
            secret_key (str): Ключ для проверки JWT токенов
            algorithm (str): Алгоритм для JWT
            public_paths (List[str], optional): Список публичных путей, не требующих аутентификации
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.auth_scheme = HTTPBearer(auto_error=False)
        self.auth_service = AuthService()
        self.public_paths = public_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/favicon.ico"
        ]
        logger.info(f"AuthMiddleware initialized with {len(self.public_paths)} public paths")

    async def __call__(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Обработка входящего запроса.

        Args:
            request (Request): Входящий запрос
            call_next (RequestResponseEndpoint): Следующий обработчик в цепочке

        Returns:
            Response: Ответ от следующего обработчика или ошибка аутентификации
        """
        path = request.url.path
        
        # Пропускаем предварительные запросы OPTIONS
        if request.method == "OPTIONS":
            return await call_next(request)

        # Пропускаем публичные пути
        if await self._is_public_path(path):
            return await call_next(request)

        try:
            # Проверяем наличие и валидность токена
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing Authorization header",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Извлекаем и проверяем токен
            token = await self._extract_token(auth_header)
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Authorization header format",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Проверяем токен и получаем данные пользователя
            user_data = await self._verify_token(token)

            # Проверяем права доступа к маршруту
            await self._check_route_access(request, user_data)

            # Добавляем данные пользователя в request.state
            request.state.user = user_data
            request.state.token = token

            # Логируем успешную аутентификацию
            logger.debug(
                f"Authenticated user {user_data.get('sub')} accessing {request.method} {path}"
            )

            # Передаем запрос дальше
            response = await call_next(request)

            # Добавляем заголовки безопасности
            self._add_security_headers(response)

            return response

        except HTTPException as e:
            logger.warning(f"Authentication error: {str(e.detail)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers
            )
        except Exception as e:
            logger.error(f"Unexpected error in auth middleware: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error during authentication"},
                headers={"WWW-Authenticate": "Bearer"}
            )

    async def _is_public_path(self, path: str) -> bool:
        """
        Проверяет, является ли путь публичным.

        Args:
            path (str): Путь запроса

        Returns:
            bool: True если путь публичный, иначе False
        """
        # Проверяем точные совпадения
        if path in self.public_paths:
            return True

        # Проверяем пути с wildcards
        for public_path in self.public_paths:
            if "*" in public_path:
                pattern = public_path.replace("*", ".*")
                if re.match(pattern, path):
                    return True

        return False

    async def _extract_token(self, auth_header: str) -> Optional[str]:
        """
        Извлекает токен из заголовка Authorization.

        Args:
            auth_header (str): Заголовок Authorization

        Returns:
            Optional[str]: JWT токен или None
        """
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]

    async def _verify_token(self, token: str) -> Dict[str, Any]:
        """
        Проверяет JWT токен и возвращает данные пользователя.

        Args:
            token (str): JWT токен

        Returns:
            Dict[str, Any]: Данные пользователя

        Raises:
            HTTPException: Если токен недействителен
        """
        try:
            # Проверяем токен локально
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Проверяем срок действия токена
            exp = payload.get("exp")
            if exp:
                now = datetime.now(timezone.utc).timestamp()
                if now > exp:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            
            # Проверяем токен через Auth Service
            is_valid = await self.auth_service.validate_token(token)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

    async def _check_route_access(
        self,
        request: Request,
        user_data: Dict[str, Any]
    ) -> None:
        """
        Проверяет права доступа пользователя к маршруту.

        Args:
            request (Request): Входящий запрос
            user_data (Dict[str, Any]): Данные пользователя из токена

        Raises:
            HTTPException: Если у пользователя нет прав доступа
        """
        path = request.url.path
        method = request.method
        
        # Получаем маршрут из базы данных
        async with AsyncSession() as session:
            route_repo = RouteRepository(session)
            route = await route_repo.get_by_path(path)
            
            if route and route.auth_required:
                # Проверяем роли пользователя
                user_roles = user_data.get("roles", [])
                required_roles = route.required_roles

                if required_roles and not any(role in user_roles for role in required_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions for this route"
                    )

                # Проверяем права доступа
                user_permissions = user_data.get("permissions", [])
                required_permissions = route.required_permissions

                if required_permissions and not any(
                    perm in user_permissions for perm in required_permissions
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions for this route"
                    )

    def _add_security_headers(self, response: Response) -> None:
        """
        Добавляет заголовки безопасности к ответу.

        Args:
            response (Response): Ответ для модификации
        """
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self';"
        }
        
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value


async def get_current_user(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> Dict[str, Any]:
    """
    Dependency для получения текущего пользователя из токена.

    Args:
        request (Request): Запрос FastAPI
        token (HTTPAuthorizationCredentials): Учетные данные авторизации

    Returns:
        Dict[str, Any]: Данные текущего пользователя

    Raises:
        HTTPException: Если токен недействителен
    """
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_data = request.state.user
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user_data
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )