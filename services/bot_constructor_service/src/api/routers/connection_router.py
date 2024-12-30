from fastapi import APIRouter, Depends, status

from src.api.controllers import ConnectionController
from src.api.schemas import (
    SuccessResponse,
    ErrorResponse,
    ConnectionCreate,
    ConnectionResponse,
    ConnectionUpdate,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/connections",
    tags=["Connections"],
    dependencies=[Depends(AuthMiddleware())],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new connection between blocks",
)
async def create_connection(
    bot_id: int,
    connection: ConnectionCreate,
    connection_controller: ConnectionController = Depends(),
):
    """
    Creates a new connection between two blocks.
    """
    return await connection_controller.create_connection(bot_id, connection)


@router.get(
    "/{connection_id}",
    response_model=ConnectionResponse,
    summary="Get a connection between blocks",
)
async def get_connection(
    connection_id: int,
    connection_controller: ConnectionController = Depends(),
):
    """
    Get connection between blocks
    """
    return await connection_controller.get_connection(connection_id)

@router.put(
    "/{connection_id}",
    response_model=ConnectionResponse,
    summary="Update a connection between blocks",
)
async def update_connection(
    connection_id: int,
    connection: ConnectionUpdate,
    connection_controller: ConnectionController = Depends(),
):
    """
    Updates connection between blocks
    """
    return await connection_controller.update_connection(connection_id, connection)


@router.delete(
    "/{connection_id}",
    response_model=SuccessResponse,
    summary="Delete a connection between blocks",
)
async def delete_connection(
    connection_id: int,
    connection_controller: ConnectionController = Depends(),
):
    """
    Deletes a connection between two blocks.
    """
    return await connection_controller.delete_connection(connection_id)