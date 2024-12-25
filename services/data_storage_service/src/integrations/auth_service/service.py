# services\data_storage_service\src\integrations\auth_service\service.py
import os
from typing import Dict, Optional

import httpx
from fastapi import HTTPException
from loguru import logger


class AuthService:
    """
    Клиент для взаимодействия с внешним Auth Service.
    Отвечает за проверку прав, валидацию токенов и другие операции аутентификации.
    """

    def __init__(self, base_url: str = None):
        """
        Инициализация клиента для Auth Service.

        Args:
            base_url (str, optional): Базовый URL сервиса аутентификации.
                                    Если не указан, берется из переменных окружения.
        """
        self.base_url = base_url or os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
        if not self.base_url:
            raise ValueError(
                "Auth Service URL must be provided either in code or in environment variables."
            )
        logger.info(f"AuthService initialized with base URL: {self.base_url}")

    async def validate_token(self, token: str) -> Dict:
        """
        Проверяет валидность JWT токена через Auth Service.

        Args:
            token (str): JWT токен для проверки.

        Returns:
            Dict: Данные пользователя из токена.

        Raises:
            HTTPException: Если токен недействителен или произошла ошибка.
        """
        url = f"{self.base_url}/auth/validate-token"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers)
                
            if response.status_code != 200:
                logger.error(f"Token validation failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Token validation failed"
                )
                
            return response.json()

        except httpx.RequestError as e:
            logger.error(f"Error validating token: {str(e)}")
            raise HTTPException(status_code=500, detail="Error validating token")

    async def validate_user_permissions(self, user_id: int, permission: str) -> bool:
        """
        Проверяет наличие у пользователя определенных прав.

        Args:
            user_id (int): ID пользователя.
            permission (str): Проверяемое разрешение.

        Returns:
            bool: True если у пользователя есть права, иначе False.

        Raises:
            HTTPException: При ошибке проверки прав.
        """
        url = f"{self.base_url}/permissions/validate"
        payload = {"user_id": user_id, "permission": permission}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"Permission validation failed: {response.text}")
                return False

            data = response.json()
            return data.get("has_permission", False)

        except httpx.RequestError as e:
            logger.error(f"Error validating permissions: {str(e)}")
            return False

    async def get_user_details(self, user_id: int) -> Optional[Dict]:
        """
        Получает детальную информацию о пользователе.

        Args:
            user_id (int): ID пользователя.

        Returns:
            Optional[Dict]: Информация о пользователе или None при ошибке.

        Raises:
            HTTPException: При ошибке получения данных пользователя.
        """
        url = f"{self.base_url}/users/{user_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)

            if response.status_code != 200:
                logger.error(f"Failed to get user details: {response.text}")
                return None

            return response.json()

        except httpx.RequestError as e:
            logger.error(f"Error getting user details: {str(e)}")
            return None

    async def check_health(self) -> bool:
        """
        Проверяет доступность Auth Service.

        Returns:
            bool: True если сервис доступен, иначе False.
        """
        url = f"{self.base_url}/health"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
            return response.status_code == 200

        except httpx.RequestError as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Обновляет JWT токен используя refresh token.

        Args:
            refresh_token (str): Refresh token для обновления JWT.

        Returns:
            Optional[Dict]: Новые токены или None при ошибке.

        Raises:
            HTTPException: При ошибке обновления токена.
        """
        url = f"{self.base_url}/auth/refresh"
        payload = {"refresh_token": refresh_token}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                return None

            return response.json()

        except httpx.RequestError as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None