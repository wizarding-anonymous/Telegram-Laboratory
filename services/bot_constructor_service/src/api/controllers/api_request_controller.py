from typing import Dict, Any
from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.api_request_schema import (
    ApiRequestCreate,
    ApiRequestUpdate,
    ApiRequestResponse,
    ApiRequestListResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_content
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User


class ApiRequestController:
    """
    Controller for handling API request-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_api_request(
        self,
        bot_id: int,
        api_request: ApiRequestCreate,
        current_user: User = Depends(get_current_user),
    ) -> ApiRequestResponse:
        """Creates a new API request block."""

        validate_bot_id(bot_id)
        logger.info(f"Creating new API request block for bot ID: {bot_id}")

        block = await self.block_repository.create(
            bot_id=bot_id,
            type="api_request",
            content={
                "method": api_request.method,
                "url": api_request.url,
                "headers": api_request.headers,
                "params": api_request.params,
                "body": api_request.body,
            },
            user_id=current_user.id,
        )

        logger.info(f"API request block created successfully with ID: {block.id}")

        return ApiRequestResponse(
            id=block.id,
            type=block.type,
            method=block.content["method"],
            url=block.content["url"],
            headers=block.content["headers"],
            params=block.content["params"],
            body=block.content["body"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_api_request(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> ApiRequestResponse:
            """Get an API request block."""

            logger.info(f"Getting API request block with ID: {block_id}")
            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="api_request"
            )

            if not block:
                logger.error(f"API request block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            logger.info(f"API request block retrieved successfully with ID: {block.id}")

            return ApiRequestResponse(
                id=block.id,
                type=block.type,
                method=block.content["method"],
                url=block.content["url"],
                headers=block.content["headers"],
                params=block.content["params"],
                body=block.content["body"],
                created_at=block.created_at,
                updated_at=block.updated_at,
            )

    @handle_exceptions
    async def get_all_api_requests(
        self, bot_id: int,  current_user: User = Depends(get_current_user)
    ) -> ApiRequestListResponse:
            """Gets all API request blocks for a bot."""
            validate_bot_id(bot_id)
            logger.info(f"Getting all API request blocks for bot ID: {bot_id}")

            blocks = await self.block_repository.get_all(
                bot_id=bot_id, user_id=current_user.id, type="api_request"
            )
            if not blocks:
              logger.warning(f"No API request blocks found for bot ID: {bot_id}")
              return ApiRequestListResponse(items=[])
            
            logger.info(f"API request blocks retrieved successfully, count: {len(blocks)}")

            return ApiRequestListResponse(
                 items=[
                    ApiRequestResponse(
                        id=block.id,
                        type=block.type,
                        method=block.content["method"],
                        url=block.content["url"],
                        headers=block.content["headers"],
                        params=block.content["params"],
                        body=block.content["body"],
                        created_at=block.created_at,
                        updated_at=block.updated_at,
                    )
                   for block in blocks
                ]
            )

    @handle_exceptions
    async def update_api_request(
        self,
        block_id: int,
        api_request: ApiRequestUpdate,
         current_user: User = Depends(get_current_user),
    ) -> ApiRequestResponse:
        """Updates an existing API request block."""
        
        logger.info(f"Updating API request block with ID: {block_id}")
        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="api_request"
        )

        if not block:
            logger.error(f"API request block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
        
        updated_block = await self.block_repository.update(
            block_id=block_id,
            content={
               "method": api_request.method,
               "url": api_request.url,
                "headers": api_request.headers,
                "params": api_request.params,
                "body": api_request.body,
            },
        )

        logger.info(f"API request block updated successfully with ID: {updated_block.id}")
        return ApiRequestResponse(
            id=updated_block.id,
            type=updated_block.type,
            method=updated_block.content["method"],
            url=updated_block.content["url"],
            headers=updated_block.content["headers"],
            params=updated_block.content["params"],
            body=updated_block.content["body"],
            created_at=updated_block.created_at,
            updated_at=updated_block.updated_at,
        )

    @handle_exceptions
    async def delete_api_request(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
            """Deletes an API request block."""

            logger.info(f"Deleting API request block with ID: {block_id}")

            block = await self.block_repository.get(
               block_id=block_id, user_id=current_user.id, type="api_request"
            )

            if not block:
               logger.error(f"API request block with id {block_id} not found.")
               raise HTTPException(status_code=404, detail="Block not found")

            await self.block_repository.delete(block_id=block_id)
            logger.info(f"API request block deleted successfully with ID: {block_id}")