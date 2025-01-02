from typing import Dict, Optional
import httpx
from fastapi import HTTPException, status, Depends
from src.config import settings
from src.core.utils import handle_exceptions


class AuthService:
    def __init__(self):
        self.base_url = settings.AUTH_SERVICE_URL

    @handle_exceptions
    async def get_user_by_token(self, token: str) -> Optional[Dict]:
        """
        Sends a request to the Auth Service to validate the JWT token and retrieve user information.
        """
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = await client.get(
                    url=f"{self.base_url}/auth/me", headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                if e.response is not None and e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                      return None
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error communicating with Auth Service: {e}"
                    ) from e


def get_current_user(auth_service: AuthService = Depends(AuthService)):
    """
    Dependency to retrieve the current user based on the JWT token.
    """
    async def auth_dependency(token: str = Depends(AuthService)):
      return await auth_service.get_user_by_token(token)
    return auth_dependency