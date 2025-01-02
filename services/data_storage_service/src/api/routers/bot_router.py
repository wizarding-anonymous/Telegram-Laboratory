from fastapi import APIRouter, Depends, status

from src.api.controllers import BotController
from src.api.schemas import (
    BotCreate,
    BotResponse,
    BotListResponse,
    BotUpdate,
    SuccessResponse
)
from src.api.middleware.auth import auth_required

router = APIRouter(prefix="/bots", tags=["Bots"])


@router.post(
    "/",
    response_model=BotResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_required())]
)
async def create_bot(
    bot_data: BotCreate, controller: BotController = Depends()
) -> BotResponse:
    """
    Creates a new bot.
    """
    return await controller.create_bot(bot_data=bot_data)


@router.get(
    "/{bot_id}",
    response_model=BotResponse,
    dependencies=[Depends(auth_required())]
)
async def get_bot(
    bot_id: int, controller: BotController = Depends()
) -> BotResponse:
    """
    Retrieves a bot by its ID.
    """
    return await controller.get_bot(bot_id=bot_id)


@router.get(
    "/",
    response_model=BotListResponse,
     dependencies=[Depends(auth_required())]
)
async def get_all_bots(controller: BotController = Depends()) -> BotListResponse:
    """
    Retrieves all bots.
    """
    return await controller.get_all_bots()


@router.put(
    "/{bot_id}",
    response_model=BotResponse,
    dependencies=[Depends(auth_required())]
)
async def update_bot(
    bot_id: int, bot_data: BotUpdate, controller: BotController = Depends()
) -> BotResponse:
    """
    Updates an existing bot.
    """
    return await controller.update_bot(bot_id=bot_id, bot_data=bot_data)


@router.delete(
    "/{bot_id}",
    response_model=SuccessResponse,
     dependencies=[Depends(auth_required())]
)
async def delete_bot(
    bot_id: int, controller: BotController = Depends()
) -> SuccessResponse:
    """
    Deletes a bot.
    """
    return await controller.delete_bot(bot_id=bot_id)