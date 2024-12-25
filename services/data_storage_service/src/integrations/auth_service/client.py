# services\data_storage_service\src\integrations\auth_service\client.py

import os
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from loguru import logger

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Получает текущего пользователя из JWT токена.
    
    Args:
        credentials (HTTPAuthorizationCredentials): Учетные данные авторизации.
    
    Returns:
        dict: Информация о пользователе.
        
    Raises:
        HTTPException: Если токен недействителен или отсутствует.
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Получаем из переменных окружения
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id: int = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return {"user_id": user_id}
            
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