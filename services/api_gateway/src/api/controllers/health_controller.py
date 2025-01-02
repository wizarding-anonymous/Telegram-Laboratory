from fastapi import Depends
from loguru import logger

from src.api.schemas import HealthCheckResponse
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.integrations.service_discovery_client import ServiceDiscoveryClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class HealthController:
    """
    Controller for health checks and service status monitoring.
    """

    def __init__(self, service_discovery_client: ServiceDiscoveryClient = Depends()):
        self.service_discovery_client = service_discovery_client

    @handle_exceptions
    async def check_health(self) -> HealthCheckResponse:
        """
        Perform health check of the service and its dependencies.
        """
        logger.info("Performing health check...")
        try:
            service_health = await self._check_services()
            return HealthCheckResponse(
                status="ok", details=f"API Gateway service is healthy. Services health: {service_health}"
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise

    @handle_exceptions
    async def _check_services(self) -> Dict[str, str]:
        """
        Check health of registered services.
        """
        logging_client.debug("Checking health of registered services...")
        try:
            services = await self.service_discovery_client.get_services()
            if services:
                healthy_services = [service.get('name') for service in services if service.get('status') == 'healthy']
                unhealthy_services = [service.get('name') for service in services if service.get('status') != 'healthy']
                logging_client.info(f"Health check of services complete, healthy: {healthy_services}, unhealthy: {unhealthy_services}")
                return {"healthy": healthy_services, "unhealthy": unhealthy_services}
            else:
                 logging_client.warning("No services found in service discovery.")
                 return {}

        except Exception as e:
            logging_client.error(f"Error during service check: {e}")
            return {}