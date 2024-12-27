# user_dashboard/src/integrations/logging_client.py
import httpx
from app.config import settings


class GatewayClient:
    """
    Клиент для взаимодействия с API Gateway.
    """
    @staticmethod
    async def request(method: str, endpoint: str, headers: dict = None, data: dict = None, params: dict = None) -> dict:
        """
        Отправляет запрос к API Gateway.
        """
        url = f"{settings.API_GATEWAY_URL}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=settings.GATEWAY_TIMEOUT,
            )

            if response.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"Gateway request failed with status {response.status_code}: {response.text}",
                    request=response.request,
                    response=response,
                )

            return response.json()

    @staticmethod
    async def verify_token(token: str) -> dict:
        """
        Проверяет токен через API Gateway.
        """
        return await GatewayClient.request(
            method="GET",
            endpoint="/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )

    @staticmethod
    async def get_user_roles(user_id: int) -> list:
        """
        Получает роли пользователя через API Gateway.
        """
        return await GatewayClient.request(
            method="GET",
            endpoint=f"/users/{user_id}/roles"
        )

    @staticmethod
    async def get_bot_details(bot_id: int) -> dict:
        """
        Получает детали бота через API Gateway.
        """
        return await GatewayClient.request(
            method="GET",
            endpoint=f"/bots/{bot_id}"
        )
