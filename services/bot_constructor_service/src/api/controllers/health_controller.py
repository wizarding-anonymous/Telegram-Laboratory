# services\bot_constructor_service\src\api\controllers\health_controller.py
"""Health check controller for monitoring service status."""

from typing import Dict, Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session, check_db_connection  # Corrected import
from src.integrations.telegram import TelegramClient
from src.integrations.auth_service import AuthService
from src.core.utils import handle_exceptions
from src.core.utils.validators import validate_status, validate_version  # Import validators

class HealthController:
    """Controller for health checks and service status monitoring."""

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """Initialize health controller.
        
        Args:
            session: AsyncSession - Database session
        """
        self.session = session
        self.telegram_client = TelegramClient()
        self.auth_service = AuthService()

    @handle_exceptions
    async def check_health(self) -> Dict[str, Any]:
        """Perform health check of the service and its dependencies.
        
        Checks:
        - Database connection
        - Telegram API availability
        - Auth Service connection
        - Overall service status
        
        Returns:
            Dict with health check results and metrics
        """
        logger.debug("Performing health check")
        
        health_status = {
            "status": "healthy",
            "details": {
                "database": await self._check_database(),
                "telegram_api": await self._check_telegram_api(),
                "auth_service": await self._check_auth_service()
            },
            "version": "1.0.0"  # This can be dynamically set from config
        }
        
        # Validate status and version using validators
        if not validate_status(health_status["status"]):
            logger.warning("Invalid health status detected")
            health_status["status"] = "degraded"
        
        if not validate_version(health_status["version"]):
            logger.warning("Invalid version format detected")
            health_status["version"] = "0.0.0"  # default or fallback version
        
        # Calculate overall status
        if not all(
            detail["status"] == "healthy" 
            for detail in health_status["details"].values()
        ):
            health_status["status"] = "degraded"
            logger.warning("Service health check indicates degraded status")
        else:
            logger.info("Service health check completed successfully")

        return health_status

    async def _check_database(self) -> Dict[str, str]:
        """Check database connection status."""
        try:
            is_connected = await check_db_connection(self.session)  # Use connection check
            if is_connected:
                return {
                    "status": "healthy",
                    "message": "Database connection is active"
                }
            return {
                "status": "unhealthy",
                "message": "Database connection failed"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }

    async def _check_telegram_api(self) -> Dict[str, str]:
        """Check Telegram API connectivity."""
        try:
            if await self.telegram_client.check_connection():
                return {
                    "status": "healthy",
                    "message": "Telegram API is accessible"
                }
            return {
                "status": "unhealthy",
                "message": "Telegram API connection failed"
            }
        except Exception as e:
            logger.error(f"Telegram API health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Telegram API error: {str(e)}"
            }

    async def _check_auth_service(self) -> Dict[str, str]:
        """Check Auth Service availability."""
        try:
            if await self.auth_service.check_health():
                return {
                    "status": "healthy",
                    "message": "Auth Service is accessible"
                }
            return {
                "status": "unhealthy",
                "message": "Auth Service connection failed"
            }
        except Exception as e:
            logger.error(f"Auth Service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Auth Service error: {str(e)}"
            }

    @handle_exceptions
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        logger.debug("Collecting service metrics")
        
        try:
            metrics = {
                "uptime": await self._get_uptime(),
                "active_connections": await self._get_active_connections(),
                "memory_usage": await self._get_memory_usage(),
                "bot_metrics": await self._get_bot_metrics()
            }
            
            logger.info("Service metrics collected successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect service metrics: {str(e)}")
            raise

    async def _get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return 0.0

    async def _get_active_connections(self) -> int:
        """Get number of active database connections."""
        return 0

    async def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        return {
            "total": 0.0,
            "used": 0.0,
            "free": 0.0
        }

    async def _get_bot_metrics(self) -> Dict[str, int]:
        """Get metrics related to bots."""
        return {
            "total_bots": 0,
            "active_bots": 0,
            "total_blocks": 0
        }
