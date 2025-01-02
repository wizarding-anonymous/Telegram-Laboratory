from typing import List, Dict, Optional
import httpx
from fastapi import HTTPException, status
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class ServiceDiscoveryClient:
    """
    Client for interacting with the Service Discovery service.
    """
    def __init__(self):
        self.base_url = settings.SERVICE_DISCOVERY_URL

    @handle_exceptions
    async def get_services(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves a list of all registered services from the Service Discovery.
        """
        logging_client.info("Fetching all services from service discovery")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f"{self.base_url}/services/", timeout=10
                )
                response.raise_for_status()
                services = response.json()
                logging_client.debug(f"Successfully retrieved services from service discovery: {services}")
                return services
        except httpx.HTTPError as e:
             logging_client.error(f"Error during get services from service discovery: {e}")
             raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail=f"Error communicating with service discovery: {e}"
             ) from e
        except Exception as e:
           logging_client.error(f"An unexpected error occurred: {e}")
           raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Unexpected error: {e}"
                    ) from e