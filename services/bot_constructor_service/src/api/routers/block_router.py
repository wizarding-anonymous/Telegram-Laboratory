from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from src.api.schemas.block_schema import (
    BlockCreate,
    BlockUpdate,
    BlockResponse,
    BlockConnection,
    TextMessageCreate,
    TextMessageUpdate,
    TextMessageResponse,
    KeyboardCreate,
    KeyboardUpdate,
    KeyboardResponse,
    CallbackCreate,
    CallbackUpdate,
    CallbackResponse,
    ApiRequestCreate,
    ApiRequestUpdate,
    ApiRequestResponse,
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
)
from src.api.controllers import BlockController
from src.api.schemas.response_schema import SuccessResponse, ErrorResponse, PaginatedResponse
from src.integrations import get_current_user

router = APIRouter(
    prefix="/blocks",
    tags=["Blocks"],
    responses={404: {"model": ErrorResponse, "description": "Not Found"}},
)


@router.post("/", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
async def create_block(
    block_create: BlockCreate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a new block."""
    return await controller.create_block(block_create, user=current_user)


@router.get("/", response_model=PaginatedResponse[BlockResponse])
async def list_blocks(
    bot_id: int,
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    controller: BlockController = Depends(),
):
    """Gets a list of blocks for the bot."""
    return await controller.get_bot_blocks(bot_id=bot_id, user=current_user, page=page, page_size=page_size)


@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(
    block_id: int,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Gets a specific block by ID."""
    return await controller.get_block(block_id=block_id, user=current_user)


@router.put("/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: int,
    block_update: BlockUpdate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Updates an existing block."""
    return await controller.update_block(block_id=block_id, block_update=block_update, user=current_user)


@router.delete("/{block_id}", response_model=SuccessResponse)
async def delete_block(
    block_id: int,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Deletes a block by its ID."""
    return await controller.delete_block(block_id=block_id, user=current_user)


@router.post("/connections", response_model=SuccessResponse)
async def create_connection(
    connection: BlockConnection,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a connection between two blocks."""
    return await controller.create_connection(connection=connection, user=current_user)


@router.post("/text_message", response_model=TextMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_text_message_block(
    message_create: TextMessageCreate,
     current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a new text message block."""
    return await controller.create_text_message_block(message_create=message_create, user=current_user)


@router.put("/text_message/{block_id}", response_model=TextMessageResponse)
async def update_text_message_block(
    block_id: int,
    message_update: TextMessageUpdate,
     current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Updates an existing text message block."""
    return await controller.update_text_message_block(block_id=block_id, message_update=message_update, user=current_user)

@router.post("/keyboard", response_model=KeyboardResponse, status_code=status.HTTP_201_CREATED)
async def create_keyboard_block(
    keyboard_create: KeyboardCreate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a new keyboard block."""
    return await controller.create_keyboard_block(keyboard_create=keyboard_create, user=current_user)


@router.put("/keyboard/{block_id}", response_model=KeyboardResponse)
async def update_keyboard_block(
    block_id: int,
    keyboard_update: KeyboardUpdate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Updates an existing keyboard block."""
    return await controller.update_keyboard_block(block_id=block_id, keyboard_update=keyboard_update, user=current_user)


@router.post("/callback", response_model=CallbackResponse, status_code=status.HTTP_201_CREATED)
async def create_callback_block(
    callback_create: CallbackCreate,
     current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a new callback block."""
    return await controller.create_callback_block(callback_create=callback_create, user=current_user)


@router.put("/callback/{block_id}", response_model=CallbackResponse)
async def update_callback_block(
    block_id: int,
    callback_update: CallbackUpdate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Updates an existing callback block."""
    return await controller.update_callback_block(block_id=block_id, callback_update=callback_update, user=current_user)


@router.post("/api_request", response_model=ApiRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_api_request_block(
    api_request_create: ApiRequestCreate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a new api request block."""
    return await controller.create_api_request_block(api_request_create=api_request_create, user=current_user)


@router.put("/api_request/{block_id}", response_model=ApiRequestResponse)
async def update_api_request_block(
    block_id: int,
    api_request_update: ApiRequestUpdate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Updates an existing api request block."""
    return await controller.update_api_request_block(block_id=block_id, api_request_update=api_request_update, user=current_user)

@router.post("/webhook", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_block(
    webhook_create: WebhookCreate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Creates a new webhook block."""
    return await controller.create_webhook_block(webhook_create=webhook_create, user=current_user)


@router.put("/webhook/{block_id}", response_model=WebhookResponse)
async def update_webhook_block(
    block_id: int,
    webhook_update: WebhookUpdate,
    current_user: dict = Depends(get_current_user),
    controller: BlockController = Depends(),
):
    """Updates an existing webhook block."""
    return await controller.update_webhook_block(block_id=block_id, webhook_update=webhook_update, user=current_user)