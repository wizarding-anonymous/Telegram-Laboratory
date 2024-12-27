# services/user_dashboard/src/api/controllers/bot_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from services.user_dashboard.src.schemas.bot_schema import (
    BotCreate,
    BotUpdate,
    BotResponse,
)
from services.user_dashboard.src.models.bot_model import Bot
from services.user_dashboard.src.core.bot_service import (
    get_user_bots,
    create_bot,
    update_bot,
    delete_bot,
)
from services.user_dashboard.src.core.auth import get_current_user, User
from services.user_dashboard.src.db.database import get_db
from services.user_dashboard.src.integrations.logging_client import log_event

router = APIRouter(
    prefix="/bots",
    tags=["Bot Management"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[BotResponse])
async def list_bots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Получение списка всех ботов текущего пользователя.
    """
    try:
        bots = await get_user_bots(db, current_user.id)
        await log_event(db, "INFO", f"User {current_user.email} retrieved their bots list.")
        return bots
    except Exception as e:
        await log_event(db, "ERROR", f"Error fetching bots for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_new_bot(
    bot_create: BotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Создание нового бота пользователя.
    """
    try:
        new_bot = await create_bot(db, current_user.id, bot_create)
        await log_event(db, "INFO", f"User {current_user.email} created a new bot: {new_bot.name}.")
        return new_bot
    except ValueError as ve:
        await log_event(db, "WARNING", f"Bot creation failed for user {current_user.email}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        await log_event(db, "ERROR", f"Error creating bot for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/{bot_id}", response_model=dict)
async def update_existing_bot(
    bot_id: int,
    bot_update: BotUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Обновление данных существующего бота.
    """
    try:
        updated = await update_bot(db, current_user.id, bot_id, bot_update)
        if not updated:
            await log_event(db, "WARNING", f"Bot with ID {bot_id} not found for user {current_user.email}.")
            raise HTTPException(status_code=404, detail="Bot not found")
        
        await log_event(db, "INFO", f"User {current_user.email} updated bot ID {bot_id}.")
        return {"message": "Bot updated successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        await log_event(db, "ERROR", f"Error updating bot ID {bot_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{bot_id}", response_model=dict)
async def delete_existing_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Удаление существующего бота пользователя.
    """
    try:
        deleted = await delete_bot(db, current_user.id, bot_id)
        if not deleted:
            await log_event(db, "WARNING", f"Bot with ID {bot_id} not found for user {current_user.email}.")
            raise HTTPException(status_code=404, detail="Bot not found")
        
        await log_event(db, "INFO", f"User {current_user.email} deleted bot ID {bot_id}.")
        return {"message": "Bot deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        await log_event(db, "ERROR", f"Error deleting bot ID {bot_id} for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
