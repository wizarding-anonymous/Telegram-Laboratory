# services/bot_constructor_service/src/api/routers/bot_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.api.schemas.bot_schema import BotCreate, BotUpdate, BotResponse
from src.db.database import get_session
from src.api.controllers import BotController  # Импорт через пакет controllers
from src.api.schemas.response_schema import SuccessResponse, ErrorResponse
from src.integrations import get_current_user  # Обновлённый импорт через integrations/__init__.py

router = APIRouter(
    prefix="/bots",
    tags=["Bots"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Создать нового бота.
    """
    controller = BotController(session)
    return await controller.create_bot(bot_data, current_user["id"])


@router.get("/", response_model=List[BotResponse])
async def list_bots(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список ботов для текущего пользователя.
    """
    controller = BotController(session)
    return await controller.get_user_bots(current_user["id"], skip=skip, limit=limit)


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Получить бота по его ID.
    """
    controller = BotController(session)
    return await controller.get_bot(bot_id, current_user["id"])


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Обновить существующего бота.
    """
    controller = BotController(session)
    return await controller.update_bot(bot_id, bot_data, current_user["id"])


@router.delete("/{bot_id}", response_model=SuccessResponse)
async def delete_bot(
    bot_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Удалить бота по его ID.
    """
    controller = BotController(session)
    await controller.delete_bot(bot_id, current_user["id"])
    return SuccessResponse(message="Bot deleted successfully")
