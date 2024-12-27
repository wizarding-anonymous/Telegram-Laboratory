# services\user_dashboard\src\api\routers\bot_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app.schemas.bot import BotCreateRequest, BotResponse, BotUpdateRequest
from app.services.bot_service import BotService

router = APIRouter()

# Создание нового бота
@router.post("/", response_model=BotResponse, status_code=201)
async def create_bot(
    bot_data: BotCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Создает нового бота для текущего пользователя.
    """
    try:
        bot = await BotService.create_bot(
            db=db,
            user_id=current_user["id"],
            bot_data=bot_data,
        )
        return bot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Получение списка всех ботов пользователя
@router.get("/", response_model=List[BotResponse])
async def list_user_bots(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Возвращает список всех ботов текущего пользователя.
    """
    try:
        bots = await BotService.get_all_user_bots(db=db, user_id=current_user["id"])
        return bots
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Получение информации о конкретном боте
@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot_by_id(
    bot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Возвращает информацию о боте по его ID.
    """
    try:
        bot = await BotService.get_bot_by_id(db=db, bot_id=bot_id, user_id=current_user["id"])
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        return bot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Обновление данных бота
@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Обновляет данные указанного бота.
    """
    try:
        bot = await BotService.update_bot(
            db=db,
            bot_id=bot_id,
            user_id=current_user["id"],
            bot_data=bot_data,
        )
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        return bot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Удаление бота
@router.delete("/{bot_id}", status_code=204)
async def delete_bot(
    bot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Удаляет указанного бота.
    """
    try:
        success = await BotService.delete_bot(db=db, bot_id=bot_id, user_id=current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Bot not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
