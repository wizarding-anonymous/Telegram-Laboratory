from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_session
from src.db.models import Route
from src.db.repositories import RouteRepository
from src.core.utils import handle_exceptions
from src.core.utils.exceptions import DatabaseException
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class RouteManager:
    """
    Manages routing logic for the API Gateway.
    """

    def __init__(self, route_repository: RouteRepository = Depends(), session: AsyncSession = Depends(get_session)):
        self.route_repository = route_repository
        self.session = session

    @handle_exceptions
    async def create_route(self, path: str, method: str, destination_url: str, auth_required: bool) -> Dict[str, Any]:
        """Creates a new route."""
        logging_client.info(f"Creating route with path: {path}, method: {method}, destination: {destination_url}")
        try:
            route = await self.route_repository.create(
               path=path, method=method, destination_url=destination_url, auth_required=auth_required
            )
            logging_client.info(f"Route with path: {path}, method: {method}, destination: {destination_url} created successfully with ID: {route.id}")
            return route.__dict__
        except Exception as e:
            logging_client.error(f"Error creating route for path {path}: {e}")
            raise

    @handle_exceptions
    async def get_route(self, route_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a route by its ID."""
        logging_client.info(f"Getting route with ID: {route_id}")
        try:
             route = await self.route_repository.get(route_id=route_id)
             if not route:
                logging_client.warning(f"Route with ID {route_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
                )
             logging_client.info(f"Route with ID {route_id} retrieved successfully.")
             return route.__dict__
        except Exception as e:
             logging_client.error(f"Error getting route with ID {route_id}: {e}")
             raise
        

    @handle_exceptions
    async def get_all_routes(self) -> List[Dict[str, Any]]:
        """Retrieves all routes."""
        logging_client.info("Getting all routes")
        try:
            routes = await self.route_repository.get_all()
            logging_client.info(f"Successfully retrieved {len(routes)} routes")
            return [route.__dict__ for route in routes]
        except Exception as e:
            logging_client.error(f"Error getting all routes: {e}")
            raise

    @handle_exceptions
    async def update_route(
        self,
        route_id: int,
        path: Optional[str] = None,
        method: Optional[str] = None,
        destination_url: Optional[str] = None,
        auth_required: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates an existing route."""
        logging_client.info(f"Updating route with ID: {route_id}")
        try:
           route = await self.route_repository.update(
                route_id=route_id, path=path, method=method, destination_url=destination_url, auth_required=auth_required
            )
           if not route:
               logging_client.warning(f"Route with id {route_id} not found")
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
               )
           logging_client.info(f"Route with ID {route_id} updated successfully")
           return route.__dict__
        except Exception as e:
            logging_client.error(f"Error updating route with ID {route_id}: {e}")
            raise


    @handle_exceptions
    async def delete_route(self, route_id: int) -> Optional[Dict[str, Any]]:
        """Deletes a route by its ID."""
        logging_client.info(f"Deleting route with ID: {route_id}")
        try:
           route = await self.route_repository.delete(route_id=route_id)
           if not route:
               logging_client.warning(f"Route with ID {route_id} not found")
               raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
                 )
           logging_client.info(f"Route with ID: {route_id} deleted successfully")
           return route.__dict__
        except Exception as e:
            logging_client.error(f"Error deleting route with ID {route_id}: {e}")
            raise