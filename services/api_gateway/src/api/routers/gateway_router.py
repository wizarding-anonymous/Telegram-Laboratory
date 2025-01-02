from fastapi import APIRouter, Depends, status
from typing import List

from src.api.controllers import GatewayController
from src.api.schemas import (
    RouteCreate,
    RouteResponse,
    RouteUpdate,
    RouteListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/gateway/routes",
    tags=["Routes"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new route",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def create_route(
    route_data: RouteCreate, controller: GatewayController = Depends()
) -> RouteResponse:
    """
    Creates a new route for requests.
    """
    return await controller.create_route(route_data=route_data)


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
    summary="Get a specific route",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def get_route(
    route_id: int, controller: GatewayController = Depends()
) -> RouteResponse:
    """
    Retrieves a specific route using its ID.
    """
    return await controller.get_route(route_id=route_id)


@router.get(
    "",
    response_model=RouteListResponse,
    summary="Get a list of all routes",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def get_all_routes(controller: GatewayController = Depends()) -> RouteListResponse:
    """
    Returns a list of all defined routes.
    """
    return await controller.get_all_routes()


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
    summary="Update an existing route",
     dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def update_route(
    route_id: int, route_data: RouteUpdate, controller: GatewayController = Depends()
) -> RouteResponse:
    """
    Updates an existing route with new settings.
    """
    return await controller.update_route(route_id=route_id, route_data=route_data)


@router.delete(
    "/{route_id}",
    response_model=SuccessResponse,
    summary="Delete a route by ID",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def delete_route(
    route_id: int, controller: GatewayController = Depends()
) -> SuccessResponse:
    """
    Deletes a route from the system.
    """
    return await controller.delete_route(route_id=route_id)