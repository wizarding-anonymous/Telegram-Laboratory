from fastapi import APIRouter, Depends, status
from typing import List

from src.api.controllers import IntegrationController
from src.api.schemas import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
    IntegrationListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
    dependencies=[Depends(AuthMiddleware())],
)


@router.post(
    "",
    response_model=IntegrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new integration",
)
async def create_integration(
    integration_data: IntegrationCreate, controller: IntegrationController = Depends()
) -> IntegrationResponse:
    """
    Creates a new integration for the current user.
    """
    return await controller.create_integration(integration_data=integration_data)


@router.get(
    "/{integration_id}",
    response_model=IntegrationResponse,
    summary="Get an integration by its ID",
)
async def get_integration(
    integration_id: int, controller: IntegrationController = Depends()
) -> IntegrationResponse:
    """
    Retrieves a specific integration by its ID for the current user.
    """
    return await controller.get_integration(integration_id=integration_id)


@router.get(
    "",
    response_model=IntegrationListResponse,
    summary="Get a list of all integrations for the current user",
)
async def get_all_integrations(controller: IntegrationController = Depends()) -> IntegrationListResponse:
    """
    Retrieves all integrations for the current user.
    """
    return await controller.get_all_integrations()


@router.put(
    "/{integration_id}",
    response_model=IntegrationResponse,
    summary="Update an existing integration",
)
async def update_integration(
    integration_id: int, integration_data: IntegrationUpdate, controller: IntegrationController = Depends()
) -> IntegrationResponse:
    """
    Updates an existing integration with new data.
    """
    return await controller.update_integration(integration_id=integration_id, integration_data=integration_data)


@router.delete(
    "/{integration_id}",
    response_model=SuccessResponse,
    summary="Delete an integration by its ID",
)
async def delete_integration(
    integration_id: int, controller: IntegrationController = Depends()
) -> SuccessResponse:
    """
    Deletes a integration from the system by its ID for the current user.
    """
    return await controller.delete_integration(integration_id=integration_id)