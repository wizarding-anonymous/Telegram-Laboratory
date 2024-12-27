from typing import Dict, Any, Optional

import httpx
from fastapi import HTTPException, Depends
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class AuthService:
    """
    Client for interacting with the Authentication Service.
    """

    def __init__(self, client: httpx.AsyncClient = None):
        self.base_url = f"http://{settings.AUTH_SERVICE_HOST}:{settings.AUTH_SERVICE_PORT}"
        self.client = client or httpx.AsyncClient()
        logging_client.info("AuthService client initialized")

    async def _make_request(self, method: str, endpoint: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None) -> Any:
        """Makes an asynchronous request to the Auth Service."""
        url = f"{self.base_url}{endpoint}"
        logging_client.debug(f"Making {method} request to: {url}, json: {json}, headers: {headers}")
        try:
            response = await self.client.request(method, url, headers=headers, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logging_client.error(f"HTTP Error: {exc}")
            if exc.response and exc.response.text:
                 try:
                      error_details = exc.response.json()
                      logging_client.error(f"Auth Service error: {error_details}")
                      raise HTTPException(
                         status_code=exc.response.status_code, detail=f"Auth Service Error: {error_details.get('detail') or error_details}"
                       ) from exc
                 except httpx.JSONDecodeError:
                      logging_client.error(f"Invalid response from Auth Service: {exc.response.text}")
                      raise HTTPException(
                           status_code=exc.response.status_code, detail=f"Auth Service Error: Invalid response"
                       ) from exc
            raise HTTPException(
                    status_code=500, detail=f"Auth Service Error: {exc}"
            ) from exc
        except Exception as exc:
              logging_client.exception(f"Unexpected error: {exc}")
              raise HTTPException(status_code=500, detail="Internal server error") from exc

    @handle_exceptions
    async def get_user_by_token(self, token: str) -> Dict[str, Any]:
        """
        Retrieves user information using a JWT token.
        """
        logging_client.info("Retrieving user info from auth service using token")
        headers = {"Authorization": f"Bearer {token}"}
        return await self._make_request("GET", "/auth/me", headers=headers)

    @handle_exceptions
    async def check_user_permissions(self, token: str, required_permissions: List[str]) -> bool:
        """
        Checks user permissions based on a JWT token.
        """
        logging_client.info("Checking user permissions from auth service using token")
        headers = {"Authorization": f"Bearer {token}"}
        try:
             user_info = await self._make_request("GET", "/auth/me", headers=headers)
             user_roles = user_info.get("roles", [])
             if "admin" in user_roles:
                 return True
             if not user_roles:
                 return False
             for role in user_roles:
                role_permissions = role.get("permissions", [])
                if all(perm in role_permissions for perm in required_permissions):
                    return True

             return False
        except HTTPException as e:
            if e.status_code == 401: # User is not authenticated
                return False # In case of unathorized, return False instead of exception
            raise

    async def close(self) -> None:
       """Closes the httpx client"""
       if self.client:
            await self.client.aclose()
            logging_client.info("Auth service client closed")


async def get_current_user(
    auth_service: AuthService = Depends(),
) -> Dict[str, Any]:
    """
    Dependency to get the current user based on the JWT token in the Authorization header.
    """
    logging_client.info("Getting current user using auth service")
    from fastapi import Request
    from fastapi.exceptions import HTTPException

    async def get_token(request: Request) -> str:
        """Extract the token from the Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logging_client.warning("Authorization header is missing")
            raise HTTPException(status_code=401, detail="Authorization header is missing")

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                logging_client.warning(f"Invalid authorization scheme: {scheme}")
                raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            return token
        except ValueError:
            logging_client.warning(f"Malformed authorization header: {auth_header}")
            raise HTTPException(status_code=401, detail="Malformed authorization header")

    token = await get_token(Depends())

    try:
         user = await auth_service.get_user_by_token(token)
         logging_client.info(f"User with id: {user['id']} authorized successfully")
         return user
    except HTTPException as e:
       if e.status_code == 401: # Auth service returns 401 in case of unathorized user
            logging_client.warning(f"User with provided token was unauthorized")
            raise HTTPException(status_code=401, detail="Invalid or expired token") from e
       raise