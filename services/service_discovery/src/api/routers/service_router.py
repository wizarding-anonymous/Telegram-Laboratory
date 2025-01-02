from typing import List

from fastapi import APIRouter, Depends, status

from src.api.controllers import ServiceController
from src.api.schemas import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
    ServiceListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/services",
    tags=["Services"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "/register",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new service",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def register_service(
    service_data: ServiceCreate, controller: ServiceController = Depends()
) -> ServiceResponse:
    """
    Registers a new service with the given data.
    """
    return await controller.register_service(service_data=service_data)


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Get a service by its ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def get_service(
    service_id: int, controller: ServiceController = Depends()
) -> ServiceResponse:
    """
    Retrieves a service by its unique ID.
    """
    return await controller.get_service(service_id=service_id)


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="Get a list of all services",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())],
)
async def get_all_services(controller: ServiceController = Depends()) -> ServiceListResponse:
    """
    Retrieves a list of all registered services.
    """
    return await controller.get_all_services()


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Update an existing service",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def update_service(
    service_id: int, service_data: ServiceUpdate, controller: ServiceController = Depends()
) -> ServiceResponse:
    """
    Updates an existing service by its ID with new data.
    """
    return await controller.update_service(service_id=service_id, service_data=service_data)


@router.delete(
    "/{service_id}",
    response_model=SuccessResponse,
    summary="Deregister a service by its ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def delete_service(
    service_id: int, controller: ServiceController = Depends()
) -> SuccessResponse:
    """
    Deletes a service from the system by its ID.
    """
    return await controller.delete_service(service_id=service_id)