# services\auth_service\src\api\middleware\auth_middleware.py
from typing import Optional, List, Dict, Any
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from src.core.utils.security import verify_and_decode_token, PermissionType


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        algorithm: str = "HS256",
        public_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.auth_scheme = HTTPBearer(auto_error=False)
        self.public_paths = public_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/auth/register",
            "/auth/login",
            "/auth/refresh",
            "/auth/password-reset",
            "/auth/verify-email"
        ]
        logger.info(f"AuthMiddleware initialized with public paths: {self.public_paths}")

    def _create_error_response(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None
    ) -> JSONResponse:
        default_headers = {
            "WWW-Authenticate": 'Bearer realm="auth_required"',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
        if headers:
            default_headers.update(headers)

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": detail,
                "status_code": status_code,
                "error": "Authentication Error"
            },
            headers=default_headers
        )

    def is_path_public(self, path: str) -> bool:
        return path in self.public_paths

    def _extract_token_from_header(self, authorization: str) -> Optional[str]:
        logger.debug(f"Processing Authorization header: {authorization}")
        try:
            if not authorization:
                return None

            parts = authorization.split()
            if len(parts) != 2:
                logger.warning("Invalid Authorization header format: wrong number of parts")
                return None

            scheme, token = parts
            if scheme.lower() != "bearer":
                logger.warning(f"Invalid Authorization scheme: {scheme}")
                return None

            if not token or not token.strip():
                logger.warning("Empty token in Authorization header")
                return None

            return token.strip()
        except Exception as e:
            logger.error(f"Error extracting token from header: {str(e)}")
            return None

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Any:
        path = request.url.path
        method = request.method
        logger.debug(f"Processing request: {method} {path}")

        if method == "OPTIONS":
            return await call_next(request)

        if self.is_path_public(path):
            logger.debug(f"Skipping auth for public path: {path}")
            return await call_next(request)

        try:
            authorization = request.headers.get("Authorization")
            if authorization:
                logger.debug(f"Received Authorization header: {authorization}")
            else:
                logger.warning("No Authorization header found")
                return self._create_error_response(
                    HTTP_401_UNAUTHORIZED,
                    "Authorization header is required. Use 'Bearer <token>'"
                )

            token = self._extract_token_from_header(authorization)
            if not token:
                return self._create_error_response(
                    HTTP_401_UNAUTHORIZED,
                    "Invalid Authorization header format. Use 'Bearer <token>'"
                )

            try:
                payload, is_valid = verify_and_decode_token(token, expected_type="access")
                if not is_valid or not payload:
                    logger.warning("Invalid or expired token")
                    return self._create_error_response(
                        HTTP_401_UNAUTHORIZED,
                        "Invalid or expired token"
                    )

                logger.debug(f"Token successfully verified for user_id: {payload.get('sub')}")

                user_id = payload.get("sub")
                if not user_id:
                    logger.error("Token missing user ID")
                    return self._create_error_response(
                        HTTP_401_UNAUTHORIZED,
                        "Invalid token: missing user ID"
                    )

                request.state.user_id = int(user_id)
                request.state.roles = payload.get("roles", [])
                request.state.permissions = payload.get("permissions", [])
                request.state.token_payload = payload

                logger.debug(
                    f"User authenticated: id={user_id}, "
                    f"roles={request.state.roles}, "
                    f"permissions={request.state.permissions}, "
                    f"path={path}"
                )

                return await call_next(request)

            except HTTPException as e:
                logger.warning(f"Token verification failed: {e.detail}")
                return self._create_error_response(e.status_code, e.detail)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return self._create_error_response(
                HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal server error during authentication"
            )


def admin_required():
    async def check_admin(request: Request):
        user_id = getattr(request.state, "user_id", None)
        roles = getattr(request.state, "roles", [])

        if not user_id:
            logger.warning("Unauthorized access attempt to admin endpoint")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if "admin" not in roles:
            logger.warning(
                f"Access denied: User {user_id} attempted to access admin endpoint"
            )
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        logger.debug(f"Admin access granted for user {user_id}")

    return check_admin


def check_permissions(*required_permissions: str):
    async def verify_permissions(request: Request):
        user_id = getattr(request.state, "user_id", None)
        permissions = getattr(request.state, "permissions", [])

        if not user_id:
            logger.warning("Unauthorized access attempt")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid Bearer token."
            )

        if not permissions:
            logger.warning(f"No permissions found for user {user_id}")
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="No permissions found"
            )

        missing_permissions = [
            perm for perm in required_permissions
            if perm not in permissions
        ]

        if missing_permissions:
            logger.warning(
                f"Insufficient permissions for user {user_id}. "
                f"Missing: {missing_permissions}"
            )
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )

        logger.debug(
            f"Permission check passed for user {user_id}: "
            f"required={required_permissions}"
        )

    return verify_permissions
