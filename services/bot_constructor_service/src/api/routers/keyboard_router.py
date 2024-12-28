from typing import List

from fastapi import APIRouter, Depends, status

from src.api.controllers.keyboard_controller import KeyboardController
from src.api.schemas.keyboard_schema import (
    ReplyKeyboardCreate,
    ReplyKeyboardUpdate,
    ReplyKeyboardResponse,
    ReplyKeyboardListResponse,
    InlineKeyboardCreate,
    InlineKeyboardUpdate,
    InlineKeyboardResponse,
    InlineKeyboardListResponse
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/keyboards",
    tags=["Keyboards"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "/reply",
    response_model=ReplyKeyboardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reply keyboard block",
)
async def create_reply_keyboard(
    bot_id: int,
    keyboard: ReplyKeyboardCreate,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Creates a new reply keyboard block for a specific bot.
    """
    return await keyboard_controller.create_reply_keyboard(bot_id, keyboard)


@router.get(
    "/reply/{block_id}",
    response_model=ReplyKeyboardResponse,
    summary="Get a reply keyboard block",
)
async def get_reply_keyboard(
    block_id: int,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Get a reply keyboard block by its ID.
    """
    return await keyboard_controller.get_reply_keyboard(block_id)


@router.get(
    "/reply",
    response_model=ReplyKeyboardListResponse,
    summary="Get all reply keyboard blocks for a bot",
)
async def get_all_reply_keyboards(
    bot_id: int,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Get all reply keyboard blocks for a specific bot.
    """
    return await keyboard_controller.get_all_reply_keyboards(bot_id)


@router.put(
    "/reply/{block_id}",
    response_model=ReplyKeyboardResponse,
    summary="Update a reply keyboard block",
)
async def update_reply_keyboard(
    block_id: int,
    keyboard: ReplyKeyboardUpdate,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Update an existing reply keyboard block by its ID.
    """
    return await keyboard_controller.update_reply_keyboard(block_id, keyboard)


@router.delete(
    "/reply/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a reply keyboard block",
)
async def delete_reply_keyboard(
    block_id: int,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Delete a reply keyboard block by its ID.
    """
    await keyboard_controller.delete_reply_keyboard(block_id)
    return SuccessResponse(message="Reply keyboard block deleted successfully")

@router.post(
    "/inline",
    response_model=InlineKeyboardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new inline keyboard block",
)
async def create_inline_keyboard(
    bot_id: int,
    keyboard: InlineKeyboardCreate,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Creates a new inline keyboard block for a specific bot.
    """
    return await keyboard_controller.create_inline_keyboard(bot_id, keyboard)

@router.get(
    "/inline/{block_id}",
    response_model=InlineKeyboardResponse,
    summary="Get a inline keyboard block",
)
async def get_inline_keyboard(
    block_id: int,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Get a inline keyboard block by its ID.
    """
    return await keyboard_controller.get_inline_keyboard(block_id)

@router.get(
    "/inline",
    response_model=InlineKeyboardListResponse,
    summary="Get all inline keyboard blocks for a bot",
)
async def get_all_inline_keyboards(
    bot_id: int,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Get all inline keyboard blocks for a specific bot.
    """
    return await keyboard_controller.get_all_inline_keyboards(bot_id)


@router.put(
    "/inline/{block_id}",
    response_model=InlineKeyboardResponse,
    summary="Update a inline keyboard block",
)
async def update_inline_keyboard(
    block_id: int,
    keyboard: InlineKeyboardUpdate,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Update an existing inline keyboard block by its ID.
    """
    return await keyboard_controller.update_inline_keyboard(block_id, keyboard)


@router.delete(
    "/inline/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a inline keyboard block",
)
async def delete_inline_keyboard(
    block_id: int,
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Delete a inline keyboard block by its ID.
    """
    await keyboard_controller.delete_inline_keyboard(block_id)
    return SuccessResponse(message="Inline keyboard block deleted successfully")


@router.post(
    "/{block_id}/connect",
    response_model=SuccessResponse,
    summary="Connect a keyboard block to other blocks",
)
async def connect_keyboard(
    block_id: int,
    connections: List[int],
    keyboard_controller: KeyboardController = Depends(),
):
    """
    Connect a keyboard block to other blocks.
    """
    await keyboard_controller.connect_keyboard(block_id, connections)
    return SuccessResponse(message="Keyboard block connected successfully")