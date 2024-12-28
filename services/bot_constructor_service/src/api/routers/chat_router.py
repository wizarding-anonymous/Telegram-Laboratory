from fastapi import APIRouter, Depends, status
from src.api.controllers.chat_controller import ChatController
from src.api.schemas.chat_schema import (
    ChatMemberCreate,
    ChatMemberResponse,
    ChatMemberListResponse,
    ChatTitleUpdate,
    ChatDescriptionUpdate,
    ChatMessagePinUpdate,
    ChatMessageUnpinUpdate,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/chats",
    tags=["Chats"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "/members",
    response_model=ChatMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat member block",
)
async def create_chat_member(
    bot_id: int,
    chat_member: ChatMemberCreate,
    chat_controller: ChatController = Depends(),
):
    """
    Creates a new chat member block for a specific bot.
    """
    return await chat_controller.create_chat_member(bot_id, chat_member)

@router.get(
    "/members/{block_id}",
    response_model=ChatMemberResponse,
    summary="Get a chat member block",
)
async def get_chat_member(
    block_id: int,
    chat_controller: ChatController = Depends(),
):
    """
    Get a chat member block by its ID.
    """
    return await chat_controller.get_chat_member(block_id)

@router.get(
    "/members",
    response_model=ChatMemberListResponse,
    summary="Get all chat member blocks for a bot",
)
async def get_all_chat_members(
    bot_id: int,
    chat_controller: ChatController = Depends(),
):
    """
    Get all chat member blocks for a specific bot.
    """
    return await chat_controller.get_all_chat_members(bot_id)


@router.put(
    "/members/{block_id}",
    response_model=ChatMemberResponse,
    summary="Update a chat member block",
)
async def update_chat_member(
    block_id: int,
    chat_member: ChatMemberCreate,
    chat_controller: ChatController = Depends(),
):
    """
    Update an existing chat member block by its ID.
    """
    return await chat_controller.update_chat_member(block_id, chat_member)


@router.delete(
    "/members/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a chat member block",
)
async def delete_chat_member(
    block_id: int,
    chat_controller: ChatController = Depends(),
):
    """
    Delete a chat member block by its ID.
    """
    await chat_controller.delete_chat_member(block_id)
    return SuccessResponse(message="Chat member block deleted successfully")


@router.post(
    "/title",
    response_model=SuccessResponse,
    summary="Update chat title",
)
async def update_chat_title(
    bot_id: int,
    chat_title: ChatTitleUpdate,
    chat_controller: ChatController = Depends(),
):
    """
    Updates the title of a chat.
    """
    await chat_controller.update_chat_title(bot_id, chat_title)
    return SuccessResponse(message="Chat title updated successfully")


@router.post(
    "/description",
    response_model=SuccessResponse,
    summary="Update chat description",
)
async def update_chat_description(
    bot_id: int,
    chat_description: ChatDescriptionUpdate,
    chat_controller: ChatController = Depends(),
):
    """
    Updates the description of a chat.
    """
    await chat_controller.update_chat_description(bot_id, chat_description)
    return SuccessResponse(message="Chat description updated successfully")


@router.post(
    "/pin_message",
    response_model=SuccessResponse,
    summary="Pin a message in chat",
)
async def update_chat_message_pin(
    bot_id: int,
    message_pin: ChatMessagePinUpdate,
    chat_controller: ChatController = Depends(),
):
    """
    Pins a message in chat.
    """
    await chat_controller.update_chat_message_pin(bot_id, message_pin)
    return SuccessResponse(message="Message pinned successfully")


@router.post(
    "/unpin_message",
    response_model=SuccessResponse,
    summary="Unpin a message in chat",
)
async def update_chat_message_unpin(
    bot_id: int,
    message_unpin: ChatMessageUnpinUpdate,
    chat_controller: ChatController = Depends(),
):
    """
    Unpins a message in chat.
    """
    await chat_controller.update_chat_message_unpin(bot_id, message_unpin)
    return SuccessResponse(message="Message unpinned successfully")