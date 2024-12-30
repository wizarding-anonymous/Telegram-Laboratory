from fastapi import APIRouter, Depends, status

from src.api.controllers.media_group_controller import MediaGroupController
from src.api.schemas import (
    MediaGroupCreate,
    MediaGroupUpdate,
    MediaGroupResponse,
    MediaGroupListResponse,
    SuccessResponse,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/media_groups",
    tags=["Media Groups"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "",
    response_model=MediaGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new media group block",
)
async def create_media_group(
    bot_id: int,
    media_group: MediaGroupCreate,
    media_group_controller: MediaGroupController = Depends(),
):
    """
    Creates a new media group block for a specific bot.
    """
    return await media_group_controller.create_media_group(bot_id, media_group)


@router.get(
    "/{block_id}",
    response_model=MediaGroupResponse,
    summary="Get a media group block",
)
async def get_media_group(
    block_id: int,
    media_group_controller: MediaGroupController = Depends(),
):
    """
    Get a media group block by its ID.
    """
    return await media_group_controller.get_media_group(block_id)

@router.get(
    "",
    response_model=MediaGroupListResponse,
    summary="Get all media group blocks for bot",
)
async def get_all_media_groups(
    bot_id: int,
    media_group_controller: MediaGroupController = Depends(),
):
    """
    Get all media group blocks for bot.
    """
    return await media_group_controller.get_all_media_groups(bot_id)


@router.put(
    "/{block_id}",
    response_model=MediaGroupResponse,
    summary="Update a media group block",
)
async def update_media_group(
    block_id: int,
    media_group: MediaGroupUpdate,
    media_group_controller: MediaGroupController = Depends(),
):
    """
    Update an existing media group block by its ID.
    """
    return await media_group_controller.update_media_group(block_id, media_group)


@router.delete(
    "/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a media group block",
)
async def delete_media_group(
    block_id: int,
    media_group_controller: MediaGroupController = Depends(),
):
    """
    Delete a media group block by its ID.
    """
    await media_group_controller.delete_media_group(block_id)
    return SuccessResponse(message="Media group block deleted successfully")