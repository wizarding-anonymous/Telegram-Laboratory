# services\data_storage_service\src\api\middleware\auth.py
import os
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Scope, Receive, Send


security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256"
    ):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "your-secret-key")
        self.algorithm = algorithm
        self.auth_scheme = HTTPBearer()

        if not self.secret_key:
            raise ValueError("SECRET_KEY must be set or passed to AuthMiddleware.")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await self.auth_scheme(request)
            if credentials is not None:
                payload = self._verify_token(credentials)
                user_data = {
                    "user_id": int(payload["sub"]),
                    "permissions": payload.get("permissions", []),
                }
                # сохраняем данные о пользователе в request.state
                request.state.user = user_data
        except HTTPException as e:
            logger.error(f"Authentication failed: {e.detail}")
            return self._unauthorized_response(e.detail, e.status_code)
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            return self._unauthorized_response("Authentication failed", 401)
        response = await call_next(request)
        return response

    def _verify_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Authorization credentials are required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            payload = jwt.decode(credentials.credentials, self.secret_key, algorithms=[self.algorithm])
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except JWTError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _unauthorized_response(self, detail: str, status_code: int):
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": detail}, status_code=status_code)

    async def check_permissions(self, user_data: dict, required_permission: str) -> bool:
        permissions = user_data.get("permissions", [])
        return required_permission in permissions


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        secret_key = os.getenv("SECRET_KEY", "your-secret-key")
        payload = jwt.decode(credentials.credentials, secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": int(user_id), "permissions": payload.get("permissions", [])}
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_auth_middleware() -> AuthMiddleware:
    return AuthMiddleware(
        app=None,
        secret_key=os.getenv("SECRET_KEY", "your-secret-key"),
        algorithm="HS256"
    )
