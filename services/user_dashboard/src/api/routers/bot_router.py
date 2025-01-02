from fastapi import APIRouter, Depends, status
from typing import List

from src.api.controllers import BotController
from src.api.schemas import (
    BotCreate,
    BotResponse,
    BotUpdate,
    BotListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/bots",
    tags=["Bots"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=BotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bot",
    dependencies=[Depends(AuthMiddleware())]
)
async def create_bot(
    bot_data: BotCreate, controller: BotController = Depends()
) -> BotResponse:
    """
    Creates a new bot for the current user.
    """
    return await controller.create_bot(bot_data=bot_data)


@router.get(
    "/{bot_id}",
    response_model=BotResponse,
    summary="Get a bot by its ID",
    dependencies=[Depends(AuthMiddleware())]
)
async def get_bot(
    bot_id: int, controller: BotController = Depends()
) -> BotResponse:
    """
    Retrieves a specific bot by its ID.
    """
    return await controller.get_bot(bot_id=bot_id)


@router.get(
    "",
    response_model=BotListResponse,
    summary="Get a list of all bots for current user",
    dependencies=[Depends(AuthMiddleware())]
)
async def get_all_bots(controller: BotController = Depends()) -> BotListResponse:
    """
    Retrieves all bots for the current user.
    """
    return await controller.get_all_bots()


@router.put(
    "/{bot_id}",
    response_model=BotResponse,
    summary="Update an existing bot",
    dependencies=[Depends(AuthMiddleware())]
)
async def update_bot(
    bot_id: int, bot_data: BotUpdate, controller: BotController = Depends()
) -> BotResponse:
    """
    Updates an existing bot with new data.
    """
    return await controller.update_bot(bot_id=bot_id, bot_data=bot_data)


@router.delete(
    "/{bot_id}",
    response_model=SuccessResponse,
    summary="Delete a bot by its ID",
    dependencies=[Depends(AuthMiddleware())]
)
async def delete_bot(
    bot_id: int, controller: BotController = Depends()
) -> SuccessResponse:
    """
    Deletes a bot by its ID.
    """
    return await controller.delete_bot(bot_id=bot_id)