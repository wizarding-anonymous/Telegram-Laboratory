from fastapi import APIRouter, Depends, status

from src.api.controllers import SchemaController
from src.api.schemas import (
    SchemaResponse,
    SuccessResponse
)
from src.api.middleware.auth import auth_required


router = APIRouter(prefix="/schemas", tags=["Schemas"])


@router.get(
    "/{bot_id}",
    response_model=SchemaResponse,
    dependencies=[Depends(auth_required())]
)
async def get_schema(
    bot_id: int, controller: SchemaController = Depends()
) -> SchemaResponse:
    """
    Retrieves the database schema for a bot.
    """
    return await controller.get_schema(bot_id=bot_id)


@router.delete(
    "/{bot_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(auth_required())]
)
async def delete_schema(
    bot_id: int, controller: SchemaController = Depends()
) -> SuccessResponse:
    """
    Deletes a database schema for a bot.
    """
    return await controller.delete_schema(bot_id=bot_id)