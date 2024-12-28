from fastapi import HTTPException, Depends
from loguru import logger

from src.api.schemas.db_schema import (
    DatabaseConnect,
    DatabaseQuery,
    DatabaseResponse,
    DatabaseListResponse,
)
from src.core.utils.helpers import handle_exceptions
from src.core.utils.validators import validate_bot_id, validate_content
from src.db.repositories import BlockRepository
from src.integrations.auth_service import get_current_user
from src.integrations.auth_service.client import User
from src.db.database import get_db_uri


class DbController:
    """
    Controller for handling database-related operations.
    """

    def __init__(self, block_repository: BlockRepository = Depends()):
        self.block_repository = block_repository

    @handle_exceptions
    async def create_db_connection(
        self,
        bot_id: int,
        db_connection: DatabaseConnect,
        current_user: User = Depends(get_current_user),
    ) -> DatabaseResponse:
        """Creates a new database connection block."""
        validate_bot_id(bot_id)
        logger.info(f"Creating new database connection block for bot ID: {bot_id}")
        
        db_uri = get_db_uri(bot_id)
        
        block = await self.block_repository.create(
            bot_id=bot_id,
            type="db_connect",
            content={"db_uri": db_uri, "connection_params": db_connection.connection_params},
            user_id=current_user.id,
        )
        
        logger.info(f"Database connection block created successfully with ID: {block.id}")
        return DatabaseResponse(
            id=block.id,
            type=block.type,
            db_uri=block.content["db_uri"],
            connection_params=block.content["connection_params"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )

    @handle_exceptions
    async def get_db_connection(
        self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> DatabaseResponse:
        """Get a database connection block."""

        logger.info(f"Getting database connection block with ID: {block_id}")
        block = await self.block_repository.get(
            block_id=block_id, user_id=current_user.id, type="db_connect"
        )

        if not block:
            logger.error(f"Database connection block with id {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")

        logger.info(f"Database connection block retrieved successfully with ID: {block.id}")
        return DatabaseResponse(
            id=block.id,
            type=block.type,
            db_uri=block.content["db_uri"],
            connection_params=block.content["connection_params"],
            created_at=block.created_at,
            updated_at=block.updated_at,
        )
        
    @handle_exceptions
    async def execute_db_query(
         self,
         bot_id: int,
         db_query: DatabaseQuery,
         current_user: User = Depends(get_current_user),
    ) -> DatabaseResponse:
            """Creates a new database query block."""
            validate_bot_id(bot_id)
            validate_content(db_query.query)
            logger.info(f"Creating new database query block for bot ID: {bot_id}")

            block = await self.block_repository.create(
                 bot_id=bot_id,
                 type="db_query",
                 content={"query": db_query.query},
                 user_id=current_user.id,
            )

            logger.info(f"Database query block created successfully with ID: {block.id}")

            return DatabaseResponse(
                id=block.id,
                type=block.type,
                db_uri=None,
                query=block.content["query"],
                created_at=block.created_at,
                updated_at=block.updated_at,
           )
    
    @handle_exceptions
    async def get_db_query(
         self,
         block_id: int,
          current_user: User = Depends(get_current_user),
    ) -> DatabaseResponse:
            """Get a database query block."""

            logger.info(f"Getting database query block with ID: {block_id}")
            block = await self.block_repository.get(
                block_id=block_id, user_id=current_user.id, type="db_query"
            )
            if not block:
               logger.error(f"Database query block with id {block_id} not found.")
               raise HTTPException(status_code=404, detail="Block not found")

            logger.info(f"Database query block retrieved successfully with ID: {block.id}")

            return DatabaseResponse(
                id=block.id,
                type=block.type,
                db_uri=None,
                query=block.content["query"],
                created_at=block.created_at,
                updated_at=block.updated_at,
            )


    @handle_exceptions
    async def get_all_db_blocks(
         self,
         bot_id: int,
          current_user: User = Depends(get_current_user),
    ) -> DatabaseListResponse:
            """Gets all db blocks for a bot."""
            validate_bot_id(bot_id)
            logger.info(f"Getting all db blocks for bot ID: {bot_id}")
            blocks = await self.block_repository.get_all(
                 bot_id=bot_id, user_id=current_user.id, type__in=["db_connect", "db_query"]
            )

            if not blocks:
               logger.warning(f"No db blocks found for bot ID: {bot_id}")
               return DatabaseListResponse(items=[])
           
            logger.info(f"DB blocks retrieved successfully, count: {len(blocks)}")

            return DatabaseListResponse(
               items=[
                  DatabaseResponse(
                       id=block.id,
                       type=block.type,
                       db_uri=block.content.get("db_uri"),
                       query=block.content.get("query"),
                       connection_params=block.content.get("connection_params"),
                       created_at=block.created_at,
                       updated_at=block.updated_at,
                    )
                    for block in blocks
                ]
           )
    
    @handle_exceptions
    async def update_db_query(
         self,
         block_id: int,
         db_query: DatabaseQuery,
        current_user: User = Depends(get_current_user),
    ) -> DatabaseResponse:
            """Updates an existing database query block."""

            validate_content(db_query.query)
            logger.info(f"Updating database query block with ID: {block_id}")
            
            block = await self.block_repository.get(
                 block_id=block_id, user_id=current_user.id, type="db_query"
            )
            if not block:
               logger.error(f"Database query block with id {block_id} not found.")
               raise HTTPException(status_code=404, detail="Block not found")

            updated_block = await self.block_repository.update(
                block_id=block_id,
                content={"query": db_query.query},
            )
            logger.info(f"Database query block updated successfully with ID: {updated_block.id}")

            return DatabaseResponse(
                id=updated_block.id,
                type=updated_block.type,
                db_uri=None,
                query=updated_block.content["query"],
                created_at=updated_block.created_at,
                updated_at=updated_block.updated_at,
            )


    @handle_exceptions
    async def delete_db_block(
         self, block_id: int,  current_user: User = Depends(get_current_user)
    ) -> None:
            """Deletes a database block (connection or query)."""

            logger.info(f"Deleting db block with ID: {block_id}")
            block = await self.block_repository.get(
                 block_id=block_id, user_id=current_user.id, type__in=["db_connect", "db_query"]
            )

            if not block:
                logger.error(f"DB block with id {block_id} not found.")
                raise HTTPException(status_code=404, detail="Block not found")

            await self.block_repository.delete(block_id=block_id)
            logger.info(f"DB block deleted successfully with ID: {block_id}")