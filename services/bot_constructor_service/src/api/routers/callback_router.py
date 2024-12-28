from typing import List

from fastapi import APIRouter, Depends, status

from src.api.controllers.callback_controller import CallbackController
from src.api.schemas.callback_schema import (
    CallbackQueryCreate,
    CallbackQueryUpdate,
    CallbackQueryResponse,
    CallbackQueryListResponse,
    CallbackResponseCreate,
    CallbackResponseUpdate,
    CallbackResponseResponse,
    CallbackResponseListResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware


router = APIRouter(
    prefix="/bots/{bot_id}/callbacks",
    tags=["Callbacks"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "/query",
    response_model=CallbackQueryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new callback query handler block",
)
async def create_callback_query(
    bot_id: int,
    callback_query: CallbackQueryCreate,
    callback_controller: CallbackController = Depends(),
):
    """
    Creates a new callback query handler block for a specific bot.
    """
    return await callback_controller.create_callback_query(bot_id, callback_query)


@router.get(
    "/query/{block_id}",
    response_model=CallbackQueryResponse,
    summary="Get a callback query handler block",
)
async def get_callback_query(
    block_id: int,
    callback_controller: CallbackController = Depends(),
):
    """
    Get a callback query handler block by its ID.
    """
    return await callback_controller.get_callback_query(block_id)


@router.get(
    "/query",
    response_model=CallbackQueryListResponse,
    summary="Get all callback query handler blocks for a bot",
)
async def get_all_callback_queries(
    bot_id: int,
    callback_controller: CallbackController = Depends(),
):
    """
    Get all callback query handler blocks for a specific bot.
    """
    return await callback_controller.get_all_callback_queries(bot_id)


@router.put(
    "/query/{block_id}",
    response_model=CallbackQueryResponse,
    summary="Update a callback query handler block",
)
async def update_callback_query(
    block_id: int,
    callback_query: CallbackQueryUpdate,
    callback_controller: CallbackController = Depends(),
):
    """
    Update an existing callback query handler block by its ID.
    """
    return await callback_controller.update_callback_query(block_id, callback_query)


@router.delete(
    "/query/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a callback query handler block",
)
async def delete_callback_query(
    block_id: int,
    callback_controller: CallbackController = Depends(),
):
    """
    Delete a callback query handler block by its ID.
    """
    await callback_controller.delete_callback_query(block_id)
    return SuccessResponse(message="Callback query handler block deleted successfully")

@router.post(
    "/response",
    response_model=CallbackResponseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new callback response block",
)
async def create_callback_response(
    bot_id: int,
    callback_response: CallbackResponseCreate,
    callback_controller: CallbackController = Depends(),
):
    """
    Creates a new callback response block for a specific bot.
    """
    return await callback_controller.create_callback_response(bot_id, callback_response)


@router.get(
    "/response/{block_id}",
    response_model=CallbackResponseResponse,
    summary="Get a callback response block",
)
async def get_callback_response(
    block_id: int,
    callback_controller: CallbackController = Depends(),
):
    """
    Get a callback response block by its ID.
    """
    return await callback_controller.get_callback_response(block_id)


@router.get(
    "/response",
    response_model=CallbackResponseListResponse,
    summary="Get all callback response blocks for a bot",
)
async def get_all_callback_responses(
    bot_id: int,
    callback_controller: CallbackController = Depends(),
):
    """
    Get all callback response blocks for a specific bot.
    """
    return await callback_controller.get_all_callback_responses(bot_id)


@router.put(
    "/response/{block_id}",
    response_model=CallbackResponseResponse,
    summary="Update a callback response block",
)
async def update_callback_response(
    block_id: int,
    callback_response: CallbackResponseUpdate,
    callback_controller: CallbackController = Depends(),
):
    """
    Update an existing callback response block by its ID.
    """
    return await callback_controller.update_callback_response(block_id, callback_response)


@router.delete(
    "/response/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a callback response block",
)
async def delete_callback_response(
    block_id: int,
    callback_controller: CallbackController = Depends(),
):
    """
    Delete a callback response block by its ID.
    """
    await callback_controller.delete_callback_response(block_id)
    return SuccessResponse(message="Callback response block deleted successfully")


@router.post(
    "/{block_id}/connect",
    response_model=SuccessResponse,
    summary="Connect a callback block to other blocks",
)
async def connect_callback(
    block_id: int,
    connections: List[int],
    callback_controller: CallbackController = Depends(),
):
    """
    Connect a callback block to other blocks.
    """
    await callback_controller.connect_callback(block_id, connections)
    return SuccessResponse(message="Callback block connected successfully")