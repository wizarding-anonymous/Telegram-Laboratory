# services\api_gateway\src\db\repositories\route_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Route
from src.core.schemas.route import RouteCreate, RouteUpdate
from src.core.exceptions.repository import NotFoundException


class RouteRepository:
    """Repository class for managing Route entities in the database."""
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, route_data: RouteCreate) -> Route:
        """
        Create a new route in the database.
        
        Args:
            route_data: RouteCreate schema containing route data
            
        Returns:
            Created Route model instance
            
        Raises:
            None
        """
        route = Route(
            service_name=route_data.service_name,
            endpoint_url=route_data.endpoint_url,
            http_method=route_data.http_method,
            is_active=route_data.is_active,
            timeout=route_data.timeout,
            retry_count=route_data.retry_count,
            rate_limit=route_data.rate_limit
        )
        self._session.add(route)
        await self._session.flush()
        return route

    async def get_by_id(self, route_id: int) -> Optional[Route]:
        """
        Get route by ID.
        
        Args:
            route_id: ID of the route to retrieve
            
        Returns:
            Route if found, None otherwise
            
        Raises:
            None
        """
        query = select(Route).where(Route.id == route_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_service_and_method(
        self, 
        service_name: str, 
        http_method: str
    ) -> Optional[Route]:
        """
        Get route by service name and HTTP method combination.
        
        Args:
            service_name: Name of the service
            http_method: HTTP method of the route
            
        Returns:
            Route if found, None otherwise
            
        Raises:
            None
        """
        query = select(Route).where(
            and_(
                Route.service_name == service_name,
                Route.http_method == http_method
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Route]:
        """
        Get all routes with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Route instances
            
        Raises:
            None
        """
        query = select(Route).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_active_routes(self) -> List[Route]:
        """
        Get all active routes.
        
        Returns:
            List of active Route instances
            
        Raises:
            None
        """
        query = select(Route).where(Route.is_active == True)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(
        self, 
        route_id: int, 
        route_data: RouteUpdate
    ) -> Route:
        """
        Update an existing route.
        
        Args:
            route_id: ID of the route to update
            route_data: RouteUpdate schema containing update data
            
        Returns:
            Updated Route instance
            
        Raises:
            NotFoundException: If route with given ID is not found
        """
        route = await self.get_by_id(route_id)
        if not route:
            raise NotFoundException(f"Route with id {route_id} not found")

        update_data = route_data.dict(exclude_unset=True)
        
        if update_data:
            query = (
                update(Route)
                .where(Route.id == route_id)
                .values(**update_data)
                .returning(Route)
            )
            result = await self._session.execute(query)
            return result.scalar_one()
        return route

    async def delete(self, route_id: int) -> bool:
        """
        Delete a route by ID.
        
        Args:
            route_id: ID of the route to delete
            
        Returns:
            True if route was deleted, False if route was not found
            
        Raises:
            None
        """
        query = delete(Route).where(Route.id == route_id)
        result = await self._session.execute(query)
        return result.rowcount > 0

    async def get_filtered_routes(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[Route]:
        """
        Get routes filtered by provided criteria.
        
        Args:
            filters: Dictionary of filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Route instances matching the filters
            
        Raises:
            None
        """
        conditions = []
        for key, value in filters.items():
            if hasattr(Route, key) and value is not None:
                conditions.append(getattr(Route, key) == value)

        query = select(Route)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all())