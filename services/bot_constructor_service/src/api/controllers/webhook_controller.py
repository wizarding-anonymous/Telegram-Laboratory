from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.webhook_schema import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_webhook_url
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class WebhookController:
    """
    Controller for handling webhook-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_webhook(
        self,
        bot_id: int,
        webhook: WebhookCreate,
        current_user: User = Depends(get_current_user),
    ) -> WebhookResponse:
        """Creates a new webhook block."""

        validate_bot_id(bot_id)
        validate_webhook_url(webhook.url)
        logger.info(f"Creating new webhook block for bot ID: {bot_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="webhook",
            content={"url": webhook.url},
            user_id=current_user.id,
        )
        logger.info(f"Webhook block created successfully with ID: {block.id}")
        return WebhookResponse(
            id=block.id,
            type=block.type,
            url=block.content["url"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_webhook(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> WebhookResponse:
        """Get a webhook block."""

        logger.info(f"Getting webhook block with ID: {block_id}")
        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="webhook"
        )

        if not block:
            logger.error(f"Webhook block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
        
        logger.info(f"Webhook block retrieved successfully with ID: {block.id}")

        return WebhookResponse(
            id=block.id,
            type=block.type,
            url=block.content["url"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_all_webhooks(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> WebhookListResponse:
        """Gets all webhook blocks for a bot."""

        validate_bot_id(bot_id)
        logger.info(f"Getting all webhook blocks for bot ID: {bot_id}")

        blocks = await self.block_repository.get_all(
            bot_id=bot_id, user_id=current_user.id, type="webhook"
        )
        
        if not blocks:
            logger.warning(f"No webhook blocks found for bot ID: {bot_id}")
            return WebhookListResponse(items=[])

        logger.info(f"Webhook blocks retrieved successfully, count: {len(blocks)}")
        return WebhookListResponse(
            items=[
                WebhookResponse(
                    id=block.id,
                    type=block.type,
                    url=block.content["url"],
                    created_at=block.created_at,
                    updated_at=block.updated_at,
                )
                for block in blocks
            ]
        )

    @handle_exceptions
    async def update_webhook(
        self,
        block_id: int,
        webhook: WebhookUpdate,
         current_user: User = Depends(get_current_user),
    ) -> WebhookResponse:
        """Updates an existing webhook block."""

        validate_webhook_url(webhook.url)
        logger.info(f"Updating webhook block with ID: {block_id}")
        
        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="webhook"
        )

        if not block:
            logger.error(f"Webhook block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        updated_block = await self.block_repository.update(
           block_id=block_id, content={"url": webhook.url}
        )
        
        logger.info(f"Webhook block updated successfully with ID: {updated_block.id}")

        return WebhookResponse(
            id=updated_block.id,
            type=updated_block.type,
            url=updated_block.content["url"],
            created_at=updated_block.created_at,
            updated_at=updated_block.updated_at,
        )

    @handle_exceptions
    async def delete_webhook(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
        """Deletes a webhook block."""

        logger.info(f"Deleting webhook block with ID: {block_id}")
        block = await self.block_repository.get(
           block_id=block_id, user_id=current_user.id, type="webhook"
        )
        if not block:
            logger.error(f"Webhook block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        await self.block_repository.delete(block_id=block_id)
        logger.info(f"Webhook block deleted successfully with ID: {block_id}")