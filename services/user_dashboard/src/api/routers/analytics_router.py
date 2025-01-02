from fastapi import APIRouter, Depends, status

from src.api.controllers import AnalyticsController
from src.api.schemas import (
    AnalyticsResponse,
    AnalyticsOverviewResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.get(
    "/bots/{bot_id}",
    response_model=AnalyticsResponse,
    summary="Get analytics data for a specific bot",
    dependencies=[Depends(AuthMiddleware())],
)
async def get_bot_analytics(
    bot_id: int, controller: AnalyticsController = Depends()
) -> AnalyticsResponse:
    """
    Retrieves analytics data for a specific bot.
    """
    return await controller.get_bot_analytics(bot_id=bot_id)


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get an overview of all bot analytics",
    dependencies=[Depends(AuthMiddleware())]
)
async def get_overview_analytics(
    controller: AnalyticsController = Depends()
) -> AnalyticsOverviewResponse:
    """
    Retrieves overview analytics for all bots associated with the user.
    """
    return await controller.get_overview_analytics()