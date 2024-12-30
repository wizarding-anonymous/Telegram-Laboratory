from fastapi import APIRouter, Depends, status

from src.api.controllers import ConnectionController
from src.api.schemas import (
    SuccessResponse,
    ErrorResponse,
    ConnectionCreate,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/blocks/connections",
    tags=["Connections"],
    dependencies=[Depends(AuthMiddleware())],
     responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Block not found"},
    },
)

@router.post(
    "",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new connection between blocks",
)
async def create_connection(
    source_block_id: int,
    target_block_id: int,
    bot_logic: dict = Depends(),
    connection_controller: ConnectionController = Depends(),
):
    """
    Creates a new connection between two blocks.
    """
    return await connection_controller.create_connection(source_block_id, target_block_id, bot_logic)