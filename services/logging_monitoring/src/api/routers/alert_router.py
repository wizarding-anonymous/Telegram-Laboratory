from fastapi import APIRouter, Depends, status

from src.api.controllers import AlertController
from src.api.schemas import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    AlertListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alert rule",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def create_alert(
    alert_data: AlertCreate, controller: AlertController = Depends()
) -> AlertResponse:
    """
    Creates a new alert rule with the given data.
    """
    return await controller.create_alert(alert_data=alert_data)


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get an alert rule by its ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def get_alert(
    alert_id: int, controller: AlertController = Depends()
) -> AlertResponse:
    """
    Retrieves a specific alert rule using its ID.
    """
    return await controller.get_alert(alert_id=alert_id)


@router.get(
    "/",
    response_model=AlertListResponse,
    summary="Get a list of all alert rules",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def get_all_alerts(controller: AlertController = Depends()) -> AlertListResponse:
    """
    Retrieves a list of all alert rules in the system.
    """
    return await controller.get_all_alerts()


@router.put(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Update an existing alert rule",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def update_alert(
    alert_id: int, alert_data: AlertUpdate, controller: AlertController = Depends()
) -> AlertResponse:
    """
    Updates an existing alert rule by its ID with new data.
    """
    return await controller.update_alert(alert_id=alert_id, alert_data=alert_data)


@router.delete(
    "/{alert_id}",
    response_model=SuccessResponse,
    summary="Delete an alert rule by its ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def delete_alert(
    alert_id: int, controller: AlertController = Depends()
) -> SuccessResponse:
    """
    Deletes an alert rule from the system by its ID.
    """
    return await controller.delete_alert(alert_id=alert_id)