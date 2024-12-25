# services\bot_constructor_service\src\integrations\auth_service\client.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from src.integrations.auth_service.auth_service import AuthService
from loguru import logger

# Инициализация схемы OAuth2 для извлечения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Зависимость для получения текущего пользователя на основе JWT-токена.

    Args:
        token (str): JWT-токен, извлеченный из заголовка Authorization.

    Returns:
        Dict[str, Any]: Детали пользователя, полученные от Auth Service.

    Raises:
        HTTPException: Если токен недействителен или пользователь не имеет необходимых прав.
    """
    auth_service = AuthService()
    try:
        # Получение деталей пользователя с использованием токена
        user = await auth_service.get_user_details(token)
        return user
    except HTTPException as e:
        # Проброс исключений HTTPException для корректной обработки в FastAPI
        logger.error(f"HTTPException в get_current_user: {e.detail}")
        raise e
    except Exception as e:
        # Логирование и проброс общего исключения для недействительных токенов
        logger.error(f"Ошибка в get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные для аутентификации.",
            headers={"WWW-Authenticate": "Bearer"},
        )
