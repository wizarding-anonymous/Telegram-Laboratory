from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from datetime import datetime

from src.core.utils import handle_exceptions
from src.db.database import get_session
from src.db.repositories import UserDataRepository
from src.integrations.logging_client import LoggingClient
from src.config import settings

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)

class AnalyticsManager:
    """
    Manages analytics-related operations for the User Dashboard.
    """

    def __init__(self, session: AsyncSession = Depends(get_session), user_data_repository: UserDataRepository = Depends()):
        self.session = session
        self.user_data_repository = user_data_repository


    @handle_exceptions
    async def get_bot_analytics(self, bot_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves analytics data for a specific bot by its ID.
        """
        logging_client.info(f"Getting analytics for bot_id: {bot_id} for user_id: {user_id}")
        try:
          user_data = await self.user_data_repository.get_by_bot_id_and_user_id(bot_id=bot_id, user_id=user_id)
          if not user_data:
              logging_client.warning(f"No analytics data found for bot_id: {bot_id} and user_id: {user_id}")
              return None
          logging_client.info(f"Analytics data retrieved successfully for bot_id: {bot_id} and user_id: {user_id}")
          return {
              "total_messages": user_data.analytics.get("total_messages", 0) if user_data.analytics else 0,
              "active_users": user_data.analytics.get("active_users", 0) if user_data.analytics else 0,
              "error_count": user_data.analytics.get("error_count", 0) if user_data.analytics else 0,
              "created_at": user_data.created_at,
              "updated_at": user_data.updated_at,
              "metadata": user_data.metadata
           }
        except Exception as e:
           logging_client.error(f"Error getting bot analytics for bot_id {bot_id}: {e}")
           raise


    @handle_exceptions
    async def get_overview_analytics(self, user_id: int) -> Dict[str, Any]:
         """
         Retrieves an overview of analytics data for all bots of the current user.
         """
         logging_client.info(f"Getting overview analytics for user_id: {user_id}")
         try:
             user_data_list = await self.user_data_repository.get_all_by_user_id(user_id=user_id)
             total_messages = 0
             total_active_users = 0
             total_error_count = 0

             for user_data in user_data_list:
                if user_data.analytics:
                     total_messages += user_data.analytics.get("total_messages", 0)
                     total_active_users += user_data.analytics.get("active_users", 0)
                     total_error_count += user_data.analytics.get("error_count", 0)
             overview = {
                 "total_messages": total_messages,
                 "total_active_users": total_active_users,
                 "total_error_count": total_error_count,
             }
             logging_client.info(f"Overview analytics for user {user_id} retrieved successfully: {overview}")
             return overview
         except Exception as e:
            logging_client.error(f"Error getting overview analytics for user {user_id}: {e}")
            raise