from typing import List, Dict, Any
from fastapi import Depends, HTTPException, status
from loguru import logger

from src.api.schemas import (
    SuccessResponse,
    RouteCreate,
    RouteResponse,
    RouteUpdate,
    RouteListResponse,
)
from src.core.route_manager import RouteManager
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.api.middleware.auth import admin_required

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class GatewayController:
    """
    Controller for managing routing in API Gateway.
    """

    def __init__(self, route_manager: RouteManager = Depends()):
        self.route_manager = route_manager

    @handle_exceptions
    async def create_route(self, route_data: RouteCreate, user: dict = Depends(admin_required)) -> RouteResponse:
        """
        Creates a new route.
        """
        logging_client.info(f"Creating new route with data: {route_data}")
        try:
            route = await self.route_manager.create_route(**route_data.model_dump())
            logging_client.info(f"Route created successfully with ID: {route.id}")
            return RouteResponse(**route.model_dump())
        except Exception as e:
            logging_client.error(f"Failed to create route: {e}")
            raise

    @handle_exceptions
    async def get_route(self, route_id: int, user: dict = Depends(admin_required)) -> RouteResponse:
        """
        Retrieves a specific route by its ID.
        """
        logging_client.info(f"Getting route with ID: {route_id}")
        try:
            route = await self.route_manager.get_route(route_id=route_id)
            if not route:
               logging_client.warning(f"Route with ID {route_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Route with ID {route_id} not found",
               )
            logging_client.info(f"Route with ID: {route_id} retrieved successfully")
            return RouteResponse(**route.model_dump())
        except Exception as e:
           logging_client.error(f"Error getting route {route_id}: {e}")
           raise

    @handle_exceptions
    async def get_all_routes(self, user: dict = Depends(admin_required)) -> RouteListResponse:
        """
        Retrieves a list of all routes.
        """
        logging_client.info("Getting all routes")
        try:
           routes = await self.route_manager.get_all_routes()
           logging_client.info(f"Successfully retrieved {len(routes)} routes")
           return RouteListResponse(items=[RouteResponse(**route.model_dump()) for route in routes])
        except Exception as e:
             logging_client.error(f"Error getting all routes: {e}")
             raise

    @handle_exceptions
    async def update_route(self, route_id: int, route_data: RouteUpdate, user: dict = Depends(admin_required)) -> RouteResponse:
        """
        Updates an existing route.
        """
        logging_client.info(f"Updating route with ID: {route_id}, data: {route_data}")
        try:
           route = await self.route_manager.update_route(
                route_id=route_id, **route_data.model_dump(exclude_unset=True)
            )
           if not route:
                logging_client.warning(f"Route with ID {route_id} not found for update")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Route with ID {route_id} not found"
                )
           logging_client.info(f"Route with ID {route_id} updated successfully")
           return RouteResponse(**route.model_dump())
        except Exception as e:
           logging_client.error(f"Error updating route with ID {route_id}: {e}")
           raise
    

    @handle_exceptions
    async def delete_route(self, route_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Deletes a route by its ID.
        """
        logging_client.info(f"Deleting route with ID: {route_id}")
        try:
           route = await self.route_manager.delete_route(route_id=route_id)
           if not route:
                logging_client.warning(f"Route with ID {route_id} not found for deletion")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Route with ID {route_id} not found"
                )
           logging_client.info(f"Route with ID {route_id} deleted successfully.")
           return SuccessResponse(message="Route deleted successfully")
        except Exception as e:
            logging_client.error(f"Error deleting route {route_id}: {e}")
            raise