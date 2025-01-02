from typing import List, Dict, Any
from fastapi import Depends, HTTPException, status
from loguru import logger

from src.core.alert_manager import AlertManager
from src.api.schemas import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    AlertListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient
from src.config import settings
from src.api.middleware.auth import admin_required

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AlertController:
    """
    Controller for managing alert rules in the Logging and Monitoring service.
    """

    def __init__(self, alert_manager: AlertManager = Depends()):
        self.alert_manager = alert_manager

    @handle_exceptions
    async def create_alert(self, alert_data: AlertCreate, user: dict = Depends(admin_required)) -> AlertResponse:
        """
        Creates a new alert rule.
        """
        logging_client.info(f"Creating new alert rule with data: {alert_data}")
        try:
            alert = await self.alert_manager.create_alert(**alert_data.model_dump())
            logging_client.info(f"Alert rule created successfully with ID: {alert.id}")
            return AlertResponse(**alert.__dict__)
        except Exception as e:
            logging_client.error(f"Failed to create alert rule: {e}")
            raise

    @handle_exceptions
    async def get_alert(self, alert_id: int, user: dict = Depends(admin_required)) -> AlertResponse:
        """
        Retrieves a specific alert rule by its ID.
        """
        logging_client.info(f"Getting alert rule with ID: {alert_id}")
        try:
            alert = await self.alert_manager.get_alert(alert_id=alert_id)
            if not alert:
                logging_client.warning(f"Alert rule with ID {alert_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
                )
            logging_client.info(f"Alert rule retrieved successfully with ID: {alert.id}")
            return AlertResponse(**alert.__dict__)
        except Exception as e:
            logging_client.error(f"Error getting alert with ID {alert_id}: {e}")
            raise

    @handle_exceptions
    async def get_all_alerts(self, user: dict = Depends(admin_required)) -> AlertListResponse:
        """
        Retrieves a list of all alert rules.
        """
        logging_client.info("Getting all alert rules")
        try:
            alerts = await self.alert_manager.get_all_alerts()
            logging_client.info(f"Successfully retrieved {len(alerts)} alert rules.")
            return AlertListResponse(items=[AlertResponse(**alert.__dict__) for alert in alerts])
        except Exception as e:
            logging_client.error(f"Error getting all alert rules: {e}")
            raise

    @handle_exceptions
    async def update_alert(self, alert_id: int, alert_data: AlertUpdate, user: dict = Depends(admin_required)) -> AlertResponse:
        """
        Updates an existing alert rule.
        """
        logging_client.info(f"Updating alert rule with ID: {alert_id}, data: {alert_data}")
        try:
            alert = await self.alert_manager.update_alert(
                alert_id=alert_id, **alert_data.model_dump(exclude_unset=True)
            )
            if not alert:
                logging_client.warning(f"Alert rule with ID {alert_id} not found for update.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
                )
            logging_client.info(f"Alert rule with ID {alert_id} updated successfully.")
            return AlertResponse(**alert.__dict__)
        except Exception as e:
           logging_client.error(f"Error updating alert with ID {alert_id}: {e}")
           raise

    @handle_exceptions
    async def delete_alert(self, alert_id: int, user: dict = Depends(admin_required)) -> SuccessResponse:
        """
        Deletes an alert rule by its ID.
        """
        logging_client.info(f"Deleting alert rule with ID: {alert_id}")
        try:
            alert = await self.alert_manager.delete_alert(alert_id=alert_id)
            if not alert:
                logging_client.warning(f"Alert rule with ID {alert_id} not found.")
                raise HTTPException(
                   status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
                )
            logging_client.info(f"Alert rule with ID {alert_id} deleted successfully.")
            return SuccessResponse(message="Alert rule deleted successfully")
        except Exception as e:
           logging_client.error(f"Error deleting alert with ID {alert_id}: {e}")
           raise