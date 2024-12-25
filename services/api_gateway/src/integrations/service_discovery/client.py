# services\api_gateway\src\integrations\service_discovery\client.py
from typing import Optional, List, Dict, Any
import aiohttp
from aiohttp import ClientSession
from src.core.abstractions.integrations import BaseIntegrationClient
from src.core.config import Settings
from src.core.exceptions import (
    IntegrationError,
    ServiceNotFoundError,
    ServiceValidationError,
    RegistrationError
)
from src.integrations.service_discovery.schemas import (
    Service,
    ServiceRegistration,
    ServiceUpdate,
    ServiceList,
    HealthStatus,
    ServiceMetrics
)


class ServiceDiscoveryClient(BaseIntegrationClient):
    """Client for interacting with Service Discovery service."""
    
    def __init__(self, settings: Settings, session: Optional[ClientSession] = None):
        """Initialize Service Discovery client.
        
        Args:
            settings: Application settings
            session: Optional aiohttp ClientSession
        """
        super().__init__(service_name="service_discovery")
        self.base_url = settings.service_discovery_url.rstrip('/')
        self._session = session or aiohttp.ClientSession()
        self.timeout = aiohttp.ClientTimeout(total=settings.integration_timeout)

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Service Discovery.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data
            
        Raises:
            IntegrationError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self._session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            ) as response:
                if response.status == 404:
                    raise ServiceNotFoundError(f"Service not found: {response.status}")
                elif response.status == 422:
                    raise ServiceValidationError(f"Invalid service data: {response.status}")
                elif response.status >= 400:
                    raise RegistrationError(f"Service operation failed: {response.status}")
                    
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise IntegrationError(f"Service Discovery request failed: {str(e)}")

    async def register_service(self, registration: ServiceRegistration) -> Service:
        """Register a new service instance.
        
        Args:
            registration: Service registration data
            
        Returns:
            Registered service instance
            
        Raises:
            ServiceValidationError: If registration data is invalid
            RegistrationError: If registration fails
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "POST",
            "/services/register",
            json=registration.model_dump()
        )
        return Service(**data)

    async def deregister_service(self, service_id: str) -> None:
        """Deregister a service instance.
        
        Args:
            service_id: Service instance identifier
            
        Raises:
            ServiceNotFoundError: If service not found
            RegistrationError: If deregistration fails
            IntegrationError: If request fails
        """
        await self._make_request("DELETE", f"/services/{service_id}")

    async def get_service(self, service_id: str) -> Service:
        """Get service instance by ID.
        
        Args:
            service_id: Service instance identifier
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotFoundError: If service not found
            IntegrationError: If request fails
        """
        data = await self._make_request("GET", f"/services/{service_id}")
        return Service(**data)

    async def list_services(
        self,
        service_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> ServiceList:
        """Get list of registered services with optional filtering.
        
        Args:
            service_type: Optional service type filter
            status: Optional status filter
            
        Returns:
            List of services
            
        Raises:
            IntegrationError: If request fails
        """
        params = {}
        if service_type:
            params["type"] = service_type
        if status:
            params["status"] = status
            
        data = await self._make_request("GET", "/services", params=params)
        return ServiceList(**data)

    async def update_service_status(
        self,
        service_id: str,
        status: HealthStatus
    ) -> Service:
        """Update service health status.
        
        Args:
            service_id: Service instance identifier
            status: New health status
            
        Returns:
            Updated service instance
            
        Raises:
            ServiceNotFoundError: If service not found
            ServiceValidationError: If status is invalid
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "PUT",
            f"/services/{service_id}/status",
            json=status.model_dump()
        )
        return Service(**data)

    async def update_service(
        self,
        service_id: str,
        update_data: ServiceUpdate
    ) -> Service:
        """Update service instance details.
        
        Args:
            service_id: Service instance identifier
            update_data: Service update data
            
        Returns:
            Updated service instance
            
        Raises:
            ServiceNotFoundError: If service not found
            ServiceValidationError: If update data is invalid
            IntegrationError: If request fails
        """
        data = await self._make_request(
            "PUT",
            f"/services/{service_id}",
            json=update_data.model_dump(exclude_unset=True)
        )
        return Service(**data)

    async def get_service_metrics(
        self,
        service_id: str,
        time_range: Optional[str] = None
    ) -> ServiceMetrics:
        """Get service metrics.
        
        Args:
            service_id: Service instance identifier
            time_range: Optional time range for metrics
            
        Returns:
            Service metrics
            
        Raises:
            ServiceNotFoundError: If service not found
            IntegrationError: If request fails
        """
        params = {"time_range": time_range} if time_range else {}
        data = await self._make_request(
            "GET",
            f"/services/{service_id}/metrics",
            params=params
        )
        return ServiceMetrics(**data)

    async def discover_service(
        self,
        service_type: str,
        preferred_status: Optional[str] = "healthy"
    ) -> Service:
        """Discover available service instance by type.
        
        Args:
            service_type: Type of service to discover
            preferred_status: Preferred health status
            
        Returns:
            Available service instance
            
        Raises:
            ServiceNotFoundError: If no suitable service found
            IntegrationError: If request fails
        """
        params = {"type": service_type, "status": preferred_status}
        data = await self._make_request("GET", "/services/discover", params=params)
        return Service(**data)

    async def heartbeat(self, service_id: str) -> None:
        """Send service heartbeat.
        
        Args:
            service_id: Service instance identifier
            
        Raises:
            ServiceNotFoundError: If service not found
            IntegrationError: If request fails
        """
        await self._make_request("POST", f"/services/{service_id}/heartbeat")

    async def healthcheck(self) -> bool:
        """Check Service Discovery health.
        
        Returns:
            True if service is healthy
            
        Raises:
            IntegrationError: If health check fails
        """
        try:
            await self._make_request("GET", "/health")
            return True
        except IntegrationError:
            return False