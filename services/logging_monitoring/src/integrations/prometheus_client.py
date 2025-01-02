from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from loguru import logger

from src.config import settings
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class PrometheusClient:
    """
    Client for interacting with Prometheus.
    """

    def __init__(self):
        self.base_url = settings.PROMETHEUS_URL

    @handle_exceptions
    async def push_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Pushes metrics to Prometheus Pushgateway.
        """
        logging_client.debug(f"Pushing metrics to Prometheus: {metrics}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                   url=f"{self.base_url}/metrics",
                   data="\n".join(f"{key} {value}" for key, value in metrics.items()),
                    timeout=10
                )
                response.raise_for_status()
                logging_client.debug("Metrics pushed to Prometheus successfully.")
        except httpx.HTTPError as e:
            logging_client.error(f"Error pushing metrics to Prometheus: {e}")
            raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=f"Error pushing metrics to Prometheus: {e}"
            ) from e
        except Exception as e:
             logging_client.error(f"An unexpected error occurred: {e}")
             raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected error: {e}"
                ) from e


    @handle_exceptions
    async def check_connection(self) -> bool:
        """
        Checks connection to Prometheus.
        """
        logging_client.debug("Checking connection to Prometheus.")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f"{self.base_url}/",
                     timeout=10
                )
                response.raise_for_status()
                logging_client.debug("Connection to Prometheus is healthy.")
                return True
        except httpx.HTTPError as e:
            logging_client.error(f"Connection to Prometheus failed: {e}")
            return False
        except Exception as e:
            logging_client.error(f"An unexpected error occurred: {e}")
            return False