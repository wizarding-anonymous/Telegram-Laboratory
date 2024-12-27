# services\user_dashboard\src\api\middleware\auth_middleware.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import httpx
from app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки JWT токенов через Auth Service.
    """

    def __init__(self, app):
        super().__init__(app)
        self.auth_scheme = HTTPBearer()

    async def dispatch(self, request: Request, call_next):
        if self._is_public_route(request.url.path):
            return await call_next(request)

        try:
            credentials: HTTPAuthorizationCredentials = await self.auth_scheme(request)
            if not credentials:
                raise HTTPException(status_code=401, detail="Authorization credentials missing")

            token = credentials.credentials
            user_data = await self._verify_token(token)

            # Добавляем информацию о пользователе в контекст запроса
            request.state.user = user_data

        except HTTPException as e:
            return JSONResponse({"detail": e.detail}, status_code=e.status_code)
        except Exception as e:
            return JSONResponse({"detail": str(e)}, status_code=500)

        return await call_next(request)

    async def _verify_token(self, token: str):
        """
        Проверяет JWT токен через Auth Service.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=settings.AUTH_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            return response.json()

    def _is_public_route(self, path: str) -> bool:
        """
        Проверяет, является ли маршрут публичным.
        """
        public_routes = ["/auth/login", "/auth/register", "/health"]
        return any(path.startswith(route) for route in public_routes)
