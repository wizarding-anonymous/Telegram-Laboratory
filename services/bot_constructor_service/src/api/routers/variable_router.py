from fastapi import APIRouter, Depends, status

from src.api.controllers.variable_controller import VariableController
from src.api.schemas.variable_schema import (
    VariableCreate,
    VariableUpdate,
    VariableResponse,
    VariableListResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/variables",
    tags=["Variables"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "",
    response_model=VariableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new variable block",
)
async def create_variable(
    bot_id: int,
    variable: VariableCreate,
    variable_controller: VariableController = Depends(),
):
    """
    Creates a new variable block for a specific bot.
    """
    return await variable_controller.create_variable(bot_id, variable)


@router.get(
    "/{block_id}",
    response_model=VariableResponse,
    summary="Get a variable block",
)
async def get_variable(
    block_id: int,
    variable_controller: VariableController = Depends(),
):
    """
    Get a variable block by its ID.
    """
    return await variable_controller.get_variable(block_id)


@router.get(
    "",
    response_model=VariableListResponse,
    summary="Get all variable blocks for a bot",
)
async def get_all_variables(
    bot_id: int,
    variable_controller: VariableController = Depends(),
):
    """
    Get all variable blocks for a specific bot.
    """
    return await variable_controller.get_all_variables(bot_id)


@router.put(
    "/{block_id}",
    response_model=VariableResponse,
    summary="Update a variable block",
)
async def update_variable(
    block_id: int,
    variable: VariableUpdate,
    variable_controller: VariableController = Depends(),
):
    """
    Update an existing variable block by its ID.
    """
    return await variable_controller.update_variable(block_id, variable)


@router.delete(
    "/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a variable block",
)
async def delete_variable(
    block_id: int,
    variable_controller: VariableController = Depends(),
):
    """
    Delete a variable block by its ID.
    """
    await variable_controller.delete_variable(block_id)
    return SuccessResponse(message="Variable block deleted successfully")