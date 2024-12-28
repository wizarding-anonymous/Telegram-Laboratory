from fastapi import APIRouter, Depends, status

from src.api.controllers.webhook_controller import WebhookController
from src.api.schemas.webhook_schema import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware


router = APIRouter(
    prefix="/bots/{bot_id}/webhooks",
    tags=["Webhooks"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new webhook block",
)
async def create_webhook(
    bot_id: int,
    webhook: WebhookCreate,
    webhook_controller: WebhookController = Depends(),
):
    """
    Creates a new webhook block for a specific bot.
    """
    return await webhook_controller.create_webhook(bot_id, webhook)


@router.get(
    "/{block_id}",
    response_model=WebhookResponse,
    summary="Get a webhook block",
)
async def get_webhook(
    block_id: int,
    webhook_controller: WebhookController = Depends(),
):
    """
    Get a webhook block by its ID.
    """
    return await webhook_controller.get_webhook(block_id)


@router.get(
    "",
    response_model=WebhookListResponse,
    summary="Get all webhook blocks for a bot",
)
async def get_all_webhooks(
    bot_id: int,
    webhook_controller: WebhookController = Depends(),
):
    """
    Get all webhook blocks for a specific bot.
    """
    return await webhook_controller.get_all_webhooks(bot_id)


@router.put(
    "/{block_id}",
    response_model=WebhookResponse,
    summary="Update a webhook block",
)
async def update_webhook(
    block_id: int,
    webhook: WebhookUpdate,
    webhook_controller: WebhookController = Depends(),
):
    """
    Update an existing webhook block by its ID.
    """
    return await webhook_controller.update_webhook(block_id, webhook)


@router.delete(
    "/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a webhook block",
)
async def delete_webhook(
    block_id: int,
    webhook_controller: WebhookController = Depends(),
):
    """
    Delete a webhook block by its ID.
    """
    await webhook_controller.delete_webhook(block_id)
    return SuccessResponse(message="Webhook block deleted successfully")