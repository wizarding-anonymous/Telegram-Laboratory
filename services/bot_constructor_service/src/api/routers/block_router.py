# services/bot_constructor_service/src/api/routers/block_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.api.schemas.block_schema import (
    BlockCreate,
    BlockUpdate,
    BlockResponse,
    BlockConnection,
)
from src.db.database import get_session
from src.api.controllers import BlockController  # Импорт через пакет controllers
from src.api.schemas.response_schema import SuccessResponse, ErrorResponse
from src.integrations import get_current_user  # Обновлённый импорт через integrations/__init__.py

router = APIRouter(
    prefix="/blocks",
    tags=["Blocks"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


@router.post("/", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block(
    block_data: BlockCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Создать новый блок для бота.
    """
    controller = BlockController(session)
    return await controller.create_block(block_data, current_user["id"])


@router.get("/", response_model=List[BlockResponse])
async def list_blocks(
    bot_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список блоков для конкретного бота.
    """
    controller = BlockController(session)
    return await controller.get_bot_blocks(bot_id, current_user["id"], skip=skip, limit=limit)


@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(
    block_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Получить блок по его ID.
    """
    controller = BlockController(session)
    return await controller.get_block(block_id, current_user["id"])


@router.put("/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: int,
    block_data: BlockUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Обновить существующий блок.
    """
    controller = BlockController(session)
    return await controller.update_block(block_id, block_data, current_user["id"])


@router.delete("/{block_id}", response_model=SuccessResponse)
async def delete_block(
    block_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Удалить блок по его ID.
    """
    controller = BlockController(session)
    await controller.delete_block(block_id, current_user["id"])
    return SuccessResponse(message="Block deleted successfully")


@router.post("/connections", response_model=SuccessResponse)
async def create_connection(
    connection: BlockConnection,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Создать соединение между двумя блоками.
    """
    controller = BlockController(session)
    await controller.create_connection(connection, current_user["id"])
    return SuccessResponse(message="Connection created successfully")
