from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.controllers.message_controller import MessageController
from src.api.schemas.message_schema import (
    TextMessageCreate,
    TextMessageUpdate,
    TextMessageResponse,
    TextMessageListResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/messages",
    tags=["Messages"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "/text",
    response_model=TextMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new text message block",
)
async def create_text_message(
    bot_id: int,
    text_message: TextMessageCreate,
    message_controller: MessageController = Depends(),
):
    """
    Creates a new text message block for a specific bot.
    """
    return await message_controller.create_text_message(bot_id, text_message)

@router.get(
    "/text/{block_id}",
    response_model=TextMessageResponse,
    summary="Get a text message block",
)
async def get_text_message(
    block_id: int,
    message_controller: MessageController = Depends(),
):
    """
    Get a text message block by its ID.
    """
    return await message_controller.get_text_message(block_id=block_id)

@router.get(
    "/text",
    response_model=TextMessageListResponse,
    summary="Get all text message blocks for a bot",
)
async def get_all_text_messages(
    bot_id: int,
    message_controller: MessageController = Depends(),
):
    """
    Get all text message blocks for a specific bot.
    """
    return await message_controller.get_all_text_messages(bot_id=bot_id)


@router.put(
    "/text/{block_id}",
    response_model=TextMessageResponse,
    summary="Update a text message block",
)
async def update_text_message(
    block_id: int,
    text_message: TextMessageUpdate,
    message_controller: MessageController = Depends(),
):
    """
    Update an existing text message block by its ID.
    """
    return await message_controller.update_text_message(block_id, text_message)


@router.delete(
    "/text/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a text message block",
)
async def delete_text_message(
    block_id: int,
    message_controller: MessageController = Depends(),
):
    """
    Delete a text message block by its ID.
    """
    await message_controller.delete_text_message(block_id)
    return SuccessResponse(message="Text message block deleted successfully")


@router.post(
    "/text/{block_id}/connect",
    response_model=SuccessResponse,
    summary="Connect a text message block to other blocks",
)
async def connect_text_message(
    block_id: int,
    connections: List[int],
    message_controller: MessageController = Depends(),
):
    """
    Connect a text message block to other blocks.
    """
    await message_controller.connect_text_message(block_id, connections)
    return SuccessResponse(message="Text message block connected successfully")