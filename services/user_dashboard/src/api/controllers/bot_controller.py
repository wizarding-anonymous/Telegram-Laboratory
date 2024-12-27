# services\user_dashboard\src\api\controllers\bot_controller.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_user
from services.bot_service import BotService

router = APIRouter()

# Pydantic модели для запросов и ответов
class BotCreateRequest(BaseModel):
    name: str
    description: str

class BotResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: str

class BotUpdateRequest(BaseModel):
    name: str
    description: str


# Эндпоинты
@router.post("/bots/", response_model=BotResponse)
async def create_bot(
    bot_data: BotCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Создает нового бота для текущего пользователя.
    """
    try:
        new_bot = await BotService.create_bot(
            db=db,
            user_id=user.id,
            name=bot_data.name,
            description=bot_data.description,
        )
        return new_bot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bots/", response_model=List[BotResponse])
async def get_user_bots(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Получает список ботов текущего пользователя.
    """
    try:
        bots = await BotService.get_user_bots(db=db, user_id=user.id)
        return bots
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bots/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Получает информацию о конкретном боте.
    """
    try:
        bot = await BotService.get_bot(db=db, bot_id=bot_id, user_id=user.id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        return bot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/bots/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Обновляет информацию о конкретном боте.
    """
    try:
        updated_bot = await BotService.update_bot(
            db=db,
            bot_id=bot_id,
            user_id=user.id,
            name=bot_data.name,
            description=bot_data.description,
        )
        if not updated_bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        return updated_bot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/bots/{bot_id}", status_code=204)
async def delete_bot(
    bot_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Удаляет конкретного бота.
    """
    try:
        success = await BotService.delete_bot(db=db, bot_id=bot_id, user_id=user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Bot not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
