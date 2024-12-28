from fastapi import APIRouter, Depends, status

from src.api.controllers.api_request_controller import ApiRequestController
from src.api.schemas.api_request_schema import (
    ApiRequestCreate,
    ApiRequestUpdate,
    ApiRequestResponse,
    ApiRequestListResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/api_requests",
    tags=["API Requests"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "",
    response_model=ApiRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API request block",
)
async def create_api_request(
    bot_id: int,
    api_request: ApiRequestCreate,
    api_request_controller: ApiRequestController = Depends(),
):
    """
    Creates a new API request block for a specific bot.
    """
    return await api_request_controller.create_api_request(bot_id, api_request)


@router.get(
    "/{block_id}",
    response_model=ApiRequestResponse,
    summary="Get an API request block",
)
async def get_api_request(
    block_id: int,
    api_request_controller: ApiRequestController = Depends(),
):
    """
    Get an API request block by its ID.
    """
    return await api_request_controller.get_api_request(block_id)


@router.get(
    "",
    response_model=ApiRequestListResponse,
    summary="Get all API request blocks for a bot",
)
async def get_all_api_requests(
    bot_id: int,
    api_request_controller: ApiRequestController = Depends(),
):
    """
    Get all API request blocks for a specific bot.
    """
    return await api_request_controller.get_all_api_requests(bot_id)


@router.put(
    "/{block_id}",
    response_model=ApiRequestResponse,
    summary="Update an API request block",
)
async def update_api_request(
    block_id: int,
    api_request: ApiRequestUpdate,
    api_request_controller: ApiRequestController = Depends(),
):
    """
    Update an existing API request block by its ID.
    """
    return await api_request_controller.update_api_request(block_id, api_request)


@router.delete(
    "/{block_id}",
    response_model=SuccessResponse,
    summary="Delete an API request block",
)
async def delete_api_request(
    block_id: int,
    api_request_controller: ApiRequestController = Depends(),
):
    """
    Delete an API request block by its ID.
    """
    await api_request_controller.delete_api_request(block_id)
    return SuccessResponse(message="API request block deleted successfully")