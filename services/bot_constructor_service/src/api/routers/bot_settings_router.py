from fastapi import APIRouter, Depends, status
from src.api.controllers import BotSettingsController
from src.api.schemas import (
    BotSettingsCreate,
    BotSettingsUpdate,
    BotSettingsResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/settings",
    tags=["Bot Settings"],
    dependencies=[Depends(AuthMiddleware())],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Bot not found"}
    },
)

@router.post(
    "",
    response_model=BotSettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create settings for bot",
)
async def create_bot_settings(
    bot_id: int,
    bot_settings: BotSettingsCreate,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Creates new settings for a specific bot.
    """
    return await bot_settings_controller.create_bot_settings(bot_id, bot_settings)


@router.get(
    "",
    response_model=BotSettingsResponse,
    summary="Get bot settings",
)
async def get_bot_settings(
    bot_id: int,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Gets settings of a specific bot.
    """
    return await bot_settings_controller.get_bot_settings(bot_id)


@router.put(
    "",
    response_model=BotSettingsResponse,
    summary="Update bot settings",
)
async def update_bot_settings(
    bot_id: int,
    bot_settings: BotSettingsUpdate,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Updates existing settings of a specific bot.
    """
    return await bot_settings_controller.update_bot_settings(bot_id, bot_settings)


@router.delete(
    "",
    response_model=SuccessResponse,
    summary="Delete bot settings",
)
async def delete_bot_settings(
    bot_id: int,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Deletes existing settings of a specific bot.
    """
    return await bot_settings_controller.delete_bot_settings(bot_id)