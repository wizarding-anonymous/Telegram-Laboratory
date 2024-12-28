from fastapi import APIRouter, Depends, status

from src.api.controllers.db_controller import DbController
from src.api.schemas.db_schema import (
    DatabaseConnect,
    DatabaseQuery,
    DatabaseResponse,
    DatabaseListResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/db",
    tags=["Database"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "/connect",
    response_model=DatabaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new database connection block",
)
async def create_db_connection(
    bot_id: int,
    db_connection: DatabaseConnect,
    db_controller: DbController = Depends(),
):
    """
    Creates a new database connection block for a specific bot.
    """
    return await db_controller.create_db_connection(bot_id, db_connection)


@router.get(
    "/connect/{block_id}",
    response_model=DatabaseResponse,
    summary="Get a database connection block",
)
async def get_db_connection(
    block_id: int,
    db_controller: DbController = Depends(),
):
    """
    Get a database connection block by its ID.
    """
    return await db_controller.get_db_connection(block_id)

@router.post(
    "/query",
    response_model=DatabaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new database query block",
)
async def create_db_query(
    bot_id: int,
    db_query: DatabaseQuery,
    db_controller: DbController = Depends(),
):
    """
    Creates a new database query block for a specific bot.
    """
    return await db_controller.execute_db_query(bot_id, db_query)


@router.get(
    "/query/{block_id}",
    response_model=DatabaseResponse,
    summary="Get a database query block",
)
async def get_db_query(
    block_id: int,
    db_controller: DbController = Depends(),
):
    """
    Get a database query block by its ID.
    """
    return await db_controller.get_db_query(block_id)

@router.get(
    "",
    response_model=DatabaseListResponse,
    summary="Get all db blocks for a bot",
)
async def get_all_db_blocks(
    bot_id: int,
    db_controller: DbController = Depends(),
):
    """
    Get all database blocks for a specific bot.
    """
    return await db_controller.get_all_db_blocks(bot_id)


@router.put(
    "/query/{block_id}",
    response_model=DatabaseResponse,
    summary="Update a database query block",
)
async def update_db_query(
    block_id: int,
    db_query: DatabaseQuery,
    db_controller: DbController = Depends(),
):
    """
    Update an existing database query block by its ID.
    """
    return await db_controller.update_db_query(block_id, db_query)

@router.delete(
    "/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a database block",
)
async def delete_db_block(
    block_id: int,
    db_controller: DbController = Depends(),
):
    """
    Delete a database block by its ID.
    """
    await db_controller.delete_db_block(block_id)
    return SuccessResponse(message="Database block deleted successfully")