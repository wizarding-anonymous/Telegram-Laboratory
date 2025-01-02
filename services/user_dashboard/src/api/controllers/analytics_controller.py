from typing import List, Dict
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.analytics_manager import AnalyticsManager
from src.api.schemas import (
    AnalyticsResponse,
    AnalyticsOverviewResponse,
    ErrorResponse,
)
from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.integrations.logging_client import LoggingClient
from src.api.middleware.auth import auth_required
from src.config import settings


logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AnalyticsController:
    """
    Controller for handling analytics-related operations for the User Dashboard.
    """

    def __init__(self, analytics_manager: AnalyticsManager = Depends(), session: AsyncSession = Depends(get_session)):
        self.analytics_manager = analytics_manager
        self.session = session


    @handle_exceptions
    async def get_bot_analytics(self, bot_id: int, user: dict = Depends(auth_required)) -> AnalyticsResponse:
        """
        Retrieves analytics data for a specific bot.
        """
        logging_client.info(f"Getting analytics for bot with ID: {bot_id} for user {user['id']}")
        try:
            analytics = await self.analytics_manager.get_bot_analytics(bot_id=bot_id, user_id=user['id'])
            if not analytics:
               logging_client.warning(f"No analytics data found for bot with ID {bot_id}")
               raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No analytics data found for bot with ID {bot_id}",
               )
            logging_client.info(f"Analytics data retrieved successfully for bot ID: {bot_id}")
            return AnalyticsResponse(**analytics)
        except Exception as e:
             logging_client.error(f"Error getting bot analytics data for bot {bot_id}: {e}")
             raise

    @handle_exceptions
    async def get_overview_analytics(self, user: dict = Depends(auth_required)) -> AnalyticsOverviewResponse:
        """
        Retrieves an overview of analytics data for all bots belonging to the current user.
        """
        logging_client.info(f"Getting overview analytics for user: {user['id']}")
        try:
          overview = await self.analytics_manager.get_overview_analytics(user_id=user['id'])
          logging_client.info(f"Overview analytics retrieved successfully for user {user['id']}")
          return AnalyticsOverviewResponse(**overview)
        except Exception as e:
          logging_client.error(f"Error getting overview analytics for user {user['id']}: {e}")
          raise