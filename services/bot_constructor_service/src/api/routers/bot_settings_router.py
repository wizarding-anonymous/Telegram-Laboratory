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
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=BotSettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create settings for a bot",
)
async def create_bot_settings(
    bot_id: int,
    bot_settings: BotSettingsCreate,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Creates settings for a specific bot.

    This endpoint is used to set up the initial settings for a bot, including the bot's token and telegram library.
    """
    return await bot_settings_controller.create_bot_settings(bot_id, bot_settings)


@router.get(
    "",
    response_model=BotSettingsResponse,
    summary="Get settings of a bot",
)
async def get_bot_settings(
    bot_id: int,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Gets the settings of a specific bot.

    This endpoint retrieves the settings for a specific bot.
    """
    return await bot_settings_controller.get_bot_settings(bot_id)


@router.put(
    "",
    response_model=BotSettingsResponse,
    summary="Update settings of a bot",
)
async def update_bot_settings(
    bot_id: int,
    bot_settings: BotSettingsUpdate,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Updates the settings of a specific bot.

    This endpoint is used to modify the settings of an existing bot.
    """
    return await bot_settings_controller.update_bot_settings(bot_id, bot_settings)


@router.delete(
    "",
    response_model=SuccessResponse,
    summary="Delete settings of a bot",
)
async def delete_bot_settings(
    bot_id: int,
    bot_settings_controller: BotSettingsController = Depends(),
):
    """
    Deletes the settings of a specific bot.

    This endpoint deletes the settings of a specified bot by setting it to default values.
    """
    return await bot_settings_controller.delete_bot_settings(bot_id)