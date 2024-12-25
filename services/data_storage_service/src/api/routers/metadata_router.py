# services\data_storage_service\src\api\routers\metadata_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.metadata_controller import MetadataController
from src.api.schemas.metadata_schema import (MetadataCreate, MetadataResponse,
                                             MetadataUpdate)
from src.api.schemas.response_schema import ErrorResponse, SuccessResponse
from src.db.database import apply_migrations, get_session
from src.integrations.auth_service import AuthService
from src.integrations.auth_service.client import get_current_user

router = APIRouter(
    prefix="/meta/metadata",  # Префикс для маршрутов работы с метаданными
    tags=["Metadata"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


@router.post("/", response_model=MetadataResponse, status_code=status.HTTP_201_CREATED)
async def create_metadata(
    metadata_data: MetadataCreate,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для создания метаданных для бота.

    - `metadata_data`: Данные для создания метаданных.
    - `user_id`: ID пользователя, который создает метаданные.
    """
    controller = MetadataController(session)

    # Применение миграций для базы данных бота
    try:
        # Применение миграций для базы данных бота
        await apply_migrations(metadata_data.bot_id)
        logger.info(f"Migrations applied successfully for bot {metadata_data.bot_id}")
    except Exception as e:
        logger.error(
            f"Error applying migrations for bot {metadata_data.bot_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Error applying migrations for bot's database."
        )

    return await controller.create_metadata(metadata_data, user_id)


@router.get("/{bot_id}", response_model=MetadataResponse)
async def get_metadata(
    bot_id: int,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для получения метаданных для бота по его ID.

    - `bot_id`: ID бота.
    - `user_id`: ID пользователя, запросившего метаданные.
    """
    controller = MetadataController(session)
    return await controller.get_metadata(bot_id, user_id)


@router.put("/{bot_id}", response_model=MetadataResponse)
async def update_metadata(
    bot_id: int,
    metadata_data: MetadataUpdate,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для обновления метаданных для бота.

    - `bot_id`: ID бота.
    - `metadata_data`: Данные для обновления метаданных.
    - `user_id`: ID пользователя, обновляющего метаданные.
    """
    controller = MetadataController(session)
    return await controller.update_metadata(bot_id, metadata_data, user_id)


@router.delete("/{bot_id}", response_model=SuccessResponse)
async def delete_metadata(
    bot_id: int,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для удаления метаданных для бота по его ID.

    - `bot_id`: ID бота.
    - `user_id`: ID пользователя, который удаляет метаданные.
    """
    controller = MetadataController(session)
    return await controller.delete_metadata(bot_id, user_id)
