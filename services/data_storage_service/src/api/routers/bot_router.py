# services\data_storage_service\src\api\routers\bot_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.bot_controller import BotController
from src.api.schemas.bot_schema import BotCreate, BotResponse, BotUpdate
from src.api.schemas.response_schema import ErrorResponse, SuccessResponse
from src.db.database import apply_migrations, get_session
from src.integrations.auth_service import AuthService
from src.api.middleware.auth import get_current_user

router = APIRouter(
    prefix="/meta/bots",  # Основной префикс для маршрутов
    tags=["Bots"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для создания нового бота.

    - `bot_data`: Данные для создания нового бота.
    - `user_id`: ID пользователя, создающего бота.
    """
    controller = BotController(session)
    bot = await controller.create_bot(bot_data, user_id)

    # Применение миграций для базы данных бота после его создания
    try:
        # Применение миграций для базы данных
        await apply_migrations(bot.id)
        logger.info(f"Migrations applied successfully for bot {bot.id}")
    except Exception as e:
        logger.error(f"Error applying migrations for bot {bot.id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error applying migrations for bot's database."
        )

    return bot


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для получения информации о боте по его ID.

    - `bot_id`: ID бота.
    - `user_id`: ID пользователя, запросившего информацию о боте.
    """
    controller = BotController(session)
    return await controller.get_bot(bot_id, user_id)


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для обновления данных о боте.

    - `bot_id`: ID бота.
    - `bot_data`: Данные для обновления.
    - `user_id`: ID пользователя, обновляющего данные о боте.
    """
    controller = BotController(session)
    return await controller.update_bot(bot_id, bot_data, user_id)


@router.delete("/{bot_id}", response_model=SuccessResponse)
async def delete_bot(
    bot_id: int,
    user_id: int = Depends(
        get_current_user
    ),  # Получаем текущего пользователя через токен
    session: AsyncSession = Depends(get_session),
):
    """
    Эндпоинт для удаления бота по его ID.

    - `bot_id`: ID бота.
    - `user_id`: ID пользователя, который удаляет бота.
    """
    controller = BotController(session)
    return await controller.delete_bot(bot_id, user_id)
