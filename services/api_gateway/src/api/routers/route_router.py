# services\api_gateway\src\api\routers\route_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.api.controllers.route_controller import RouteController
from src.api.schemas.route_schema import RouteCreate, RouteUpdate, RouteResponse
from src.api.schemas.response_schema import SuccessResponse
from src.api.middleware.auth import get_current_user
from src.core.utils.rate_limiter import rate_limit
from src.db.database import get_session

router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Route not found"},
        429: {"description": "Too Many Requests"},
        500: {"description": "Internal Server Error"}
    }
)

@router.post(
    "/",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new route in API Gateway",
    responses={
        201: {
            "description": "Route created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "path": "/api/v1/users",
                        "method": "GET",
                        "destination_url": "http://user-service/api/v1/users",
                        "auth_required": True,
                        "required_roles": ["admin"],
                        "required_permissions": ["read:users"]
                    }
                }
            }
        }
    }
)
@rate_limit(max_requests=10, window_seconds=60)
async def create_route(
    route_data: RouteCreate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> RouteResponse:
    """
    Creates a new route in the API Gateway.
    Requires admin privileges.
    """
    logger.info(f"Creating new route: {route_data.path} -> {route_data.destination_url}")
    controller = RouteController(session)
    return await controller.create_route(route_data, current_user["user_id"])

@router.get(
    "/",
    response_model=List[RouteResponse],
    description="Get all routes with pagination",
    responses={
        200: {
            "description": "List of routes",
            "content": {
                "application/json": {
                    "example": [{
                        "id": 1,
                        "path": "/api/v1/users",
                        "method": "GET",
                        "destination_url": "http://user-service/api/v1/users",
                        "auth_required": True
                    }]
                }
            }
        }
    }
)
async def get_routes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> List[RouteResponse]:
    """
    Retrieves all routes with pagination support.
    """
    logger.debug(f"Fetching routes with skip={skip} and limit={limit}")
    controller = RouteController(session)
    return await controller.get_routes(skip=skip, limit=limit)

@router.get(
    "/{route_id}",
    response_model=RouteResponse,
    description="Get a specific route by ID",
    responses={
        200: {
            "description": "Route details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "path": "/api/v1/users",
                        "method": "GET",
                        "destination_url": "http://user-service/api/v1/users",
                        "auth_required": True
                    }
                }
            }
        }
    }
)
async def get_route(
    route_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> RouteResponse:
    """
    Retrieves a specific route by its ID.
    """
    logger.debug(f"Fetching route with ID: {route_id}")
    controller = RouteController(session)
    return await controller.get_route(route_id)

@router.put(
    "/{route_id}",
    response_model=RouteResponse,
    description="Update an existing route",
    responses={
        200: {
            "description": "Route updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "path": "/api/v1/users",
                        "method": "GET",
                        "destination_url": "http://user-service/api/v1/users",
                        "auth_required": True,
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
        }
    }
)
@rate_limit(max_requests=10, window_seconds=60)
async def update_route(
    route_id: int,
    route_data: RouteUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> RouteResponse:
    """
    Updates an existing route.
    Requires admin privileges.
    """
    logger.info(f"Updating route {route_id}")
    controller = RouteController(session)
    return await controller.update_route(route_id, route_data, current_user["user_id"])

@router.delete(
    "/{route_id}",
    response_model=SuccessResponse,
    description="Delete a route",
    responses={
        200: {
            "description": "Route deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Route deleted successfully"
                    }
                }
            }
        }
    }
)
@rate_limit(max_requests=10, window_seconds=60)
async def delete_route(
    route_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> SuccessResponse:
    """
    Deletes a route.
    Requires admin privileges.
    """
    logger.info(f"Deleting route {route_id}")
    controller = RouteController(session)
    return await controller.delete_route(route_id, current_user["user_id"])

@router.get(
    "/by-path/{path:path}",
    response_model=RouteResponse,
    description="Get a route by its path",
    responses={
        200: {
            "description": "Route details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "path": "/api/v1/users",
                        "method": "GET",
                        "destination_url": "http://user-service/api/v1/users",
                        "auth_required": True
                    }
                }
            }
        }
    }
)
async def get_route_by_path(
    path: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> RouteResponse:
    """
    Retrieves a route by its path.
    """
    logger.debug(f"Fetching route with path: {path}")
    controller = RouteController(session)
    return await controller.get_route_by_path(path)

@router.post(
    "/{route_id}/cache",
    response_model=SuccessResponse,
    description="Cache a route for faster access",
    responses={
        200: {
            "description": "Route cached successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Route cached successfully"
                    }
                }
            }
        }
    }
)
@rate_limit(max_requests=20, window_seconds=60)
async def cache_route(
    route_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
) -> SuccessResponse:
    """
    Caches a route for faster access.
    Requires admin privileges.
    """
    logger.info(f"Caching route {route_id}")
    controller = RouteController(session)
    await controller.cache_route(route_id)
    return SuccessResponse(message="Route cached successfully")
