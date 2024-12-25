# services\bot_constructor_service\src\api\middleware\auth.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

class AuthMiddleware:
    """
    Middleware for JWT token validation and user authentication.
    """
    def __init__(self, secret_key: str, algorithm: str):
        """
        Initialize the AuthMiddleware with a secret key and algorithm.

        Args:
            secret_key (str): Secret key for decoding JWT tokens.
            algorithm (str): Algorithm used for JWT encoding and decoding.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.auth_scheme = HTTPBearer()

    async def verify_token(self, credentials: Optional[HTTPAuthorizationCredentials]) -> dict:
        """
        Verify the provided JWT token and extract its payload.

        Args:
            credentials (Optional[HTTPAuthorizationCredentials]): Authorization credentials.

        Returns:
            dict: Decoded JWT payload.

        Raises:
            HTTPException: If the token is invalid or missing.
        """
        if credentials is None:
            raise HTTPException(status_code=403, detail="Authorization credentials are required.")

        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
        except JWTError as e:
            raise HTTPException(status_code=403, detail=f"Invalid token: {str(e)}")

        return payload

    async def __call__(self, request: Request):
        """
        Middleware entry point to validate and attach user data to the request.

        Args:
            request (Request): The incoming HTTP request.
        """
        credentials: HTTPAuthorizationCredentials = await self.auth_scheme(request)
        user_data = await self.verify_token(credentials)
        request.state.user = user_data
