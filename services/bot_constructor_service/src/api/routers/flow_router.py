from fastapi import APIRouter, Depends, status

from src.api.controllers.flow_controller import FlowController
from src.api.schemas.flow_schema import (
    FlowChartCreate,
    FlowChartUpdate,
    FlowChartResponse,
)
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/bots/{bot_id}/flow",
    tags=["Flow"],
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "",
    response_model=FlowChartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new flow chart block",
)
async def create_flow_chart(
    bot_id: int,
    flow_chart: FlowChartCreate,
    flow_controller: FlowController = Depends(),
):
    """
    Creates a new flow chart block for a specific bot.
    """
    return await flow_controller.create_flow_chart(bot_id, flow_chart)


@router.get(
    "/{block_id}",
    response_model=FlowChartResponse,
    summary="Get a flow chart block",
)
async def get_flow_chart(
    block_id: int,
    flow_controller: FlowController = Depends(),
):
    """
    Get a flow chart block by its ID.
    """
    return await flow_controller.get_flow_chart(block_id)


@router.put(
    "/{block_id}",
    response_model=FlowChartResponse,
    summary="Update a flow chart block",
)
async def update_flow_chart(
    block_id: int,
    flow_chart: FlowChartUpdate,
    flow_controller: FlowController = Depends(),
):
    """
    Update an existing flow chart block by its ID.
    """
    return await flow_controller.update_flow_chart(block_id, flow_chart)


@router.delete(
    "/{block_id}",
    response_model=SuccessResponse,
    summary="Delete a flow chart block",
)
async def delete_flow_chart(
    block_id: int,
    flow_controller: FlowController = Depends(),
):
    """
    Delete a flow chart block by its ID.
    """
    await flow_controller.delete_flow_chart(block_id)
    return SuccessResponse(message="Flow chart block deleted successfully")