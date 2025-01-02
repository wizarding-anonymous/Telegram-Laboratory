# src/integrations/service_discovery/client.py
import json
from typing import Dict, Any

import httpx
from loguru import logger
from src.config import settings
from src.core.utils.exceptions import ServiceDiscoveryException


class ServiceDiscoveryClient:
    """
    Client for interacting with the Service Discovery microservice.
    """

    def __init__(self, service_name: str = settings.SERVICE_NAME):
        self.base_url = settings.SERVICE_DISCOVERY_URL
        self.service_name = service_name
        self.client = httpx.AsyncClient()

    async def register_service(self) -> str:
        """Registers the service with Service Discovery."""
        url = f"{self.base_url}/services/register"
        payload = {
            "name": self.service_name,
            "address": settings.SERVICE_HOST,
            "port": settings.SERVICE_PORT,
             "metadata": {
                "version": settings.SERVICE_VERSION
            }
        }
        try:
            logger.info(f"Registering service {self.service_name} with Service Discovery: {url}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            service_id = data.get("service_id")
            logger.info(f"Service {self.service_name} registered successfully with ID: {service_id}")
            return service_id
        except httpx.HTTPError as e:
            logger.error(f"Error registering service {self.service_name} with Service Discovery: {e}")
            raise ServiceDiscoveryException(f"Failed to register service with Service Discovery: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error registering service {self.service_name} with Service Discovery: {e}")
            raise ServiceDiscoveryException(f"Unexpected error registering service with Service Discovery: {e}") from e

    async def unregister_service(self, service_id: str) -> None:
      """Unregisters the service from Service Discovery."""
      url = f"{self.base_url}/services/{service_id}"
      try:
          logger.info(f"Unregistering service {self.service_name} with Service Discovery: {url}")
          response = await self.client.delete(url)
          response.raise_for_status()
          logger.info(f"Service {self.service_name} unregistered successfully")
      except httpx.HTTPError as e:
           logger.error(f"Error unregistering service {self.service_name} with Service Discovery: {e}")
           raise ServiceDiscoveryException(f"Failed to unregister service from Service Discovery: {e}") from e
      except Exception as e:
           logger.error(f"Unexpected error unregistering service {self.service_name} with Service Discovery: {e}")
           raise ServiceDiscoveryException(f"Unexpected error unregistering service from Service Discovery: {e}") from e



    async def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """
        Retrieves information about a specific service from Service Discovery.
        """
        url = f"{self.base_url}/services/"
        try:
            logger.info(f"Fetching info for service {service_name} from Service Discovery")
            response = await self.client.get(url)
            response.raise_for_status()
            services = response.json()
            for service in services:
                if service.get("name") == service_name:
                    logger.info(f"Info for service {service_name} fetched successfully: {service}")
                    return service
            logger.warning(f"Service {service_name} not found in Service Discovery")
            return {}
        except httpx.HTTPError as e:
            logger.error(f"Error fetching info for service {service_name} from Service Discovery: {e}")
            raise ServiceDiscoveryException(
                f"Failed to fetch service info from Service Discovery: {e}"
            ) from e
        except Exception as e:
             logger.error(f"Unexpected error fetching info for service {service_name} from Service Discovery: {e}")
             raise ServiceDiscoveryException(
                f"Unexpected error fetching service info from Service Discovery: {e}"
            ) from e
    
    async def close(self):
        """Closes the httpx client."""
        if self.client:
            await self.client.aclose()