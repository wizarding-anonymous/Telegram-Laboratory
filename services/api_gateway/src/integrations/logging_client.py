# services\api_gateway\src\integrations\logging_client.py
from typing import Optional, Dict, Any, List
import json
import logging
import aiohttp
from datetime import datetime
from aiohttp import ClientSession
from src.core.abstractions.integrations import BaseIntegrationClient
from src.core.config import Settings
from src.core.exceptions import IntegrationError


class LoggingClient(BaseIntegrationClient):
    """Client for interacting with Logging service."""
    
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    def __init__(
        self,
        settings: Settings,
        service_name: str,
        session: Optional[ClientSession] = None
    ):
        """Initialize Logging client.
        
        Args:
            settings: Application settings
            service_name: Name of the service using this client
            session: Optional aiohttp ClientSession
        """
        super().__init__(service_name="logging")
        self.base_url = settings.logging_service_url.rstrip('/')
        self._session = session or aiohttp.ClientSession()
        self.timeout = aiohttp.ClientTimeout(total=settings.integration_timeout)
        self.service_name = service_name
        self.environment = settings.environment
        self.min_level = self.LEVELS.get(settings.log_level.lower(), logging.INFO)

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
        """Make HTTP request to Logging service.
        
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
                if response.status >= 400:
                    raise IntegrationError(
                        f"Logging service request failed: {response.status}"
                    )
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise IntegrationError(f"Logging service request failed: {str(e)}")

    def _prepare_log_entry(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare log entry data.
        
        Args:
            level: Log level
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            **kwargs: Additional log entry fields
            
        Returns:
            Prepared log entry data
        """
        timestamp = datetime.utcnow().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "service": self.service_name,
            "environment": self.environment,
            "level": level.upper(),
            "message": message,
            "context": context or {},
            **kwargs
        }
        
        if correlation_id:
            log_entry["correlation_id"] = correlation_id
            
        return log_entry

    async def _log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send log entry to logging service.
        
        Args:
            level: Log level
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            **kwargs: Additional log entry fields
            
        Raises:
            IntegrationError: If logging fails
        """
        if self.LEVELS[level.lower()] < self.min_level:
            return
            
        log_entry = self._prepare_log_entry(
            level=level,
            message=message,
            context=context,
            correlation_id=correlation_id,
            **kwargs
        )
        
        await self._make_request("POST", "/logs", json=log_entry)

    async def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send debug level log.
        
        Args:
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            **kwargs: Additional log entry fields
        """
        await self._log("debug", message, context, correlation_id, **kwargs)

    async def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send info level log.
        
        Args:
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            **kwargs: Additional log entry fields
        """
        await self._log("info", message, context, correlation_id, **kwargs)

    async def warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Send warning level log.
        
        Args:
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            **kwargs: Additional log entry fields
        """
        await self._log("warning", message, context, correlation_id, **kwargs)

    async def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        exception: Optional[Exception] = None,
        **kwargs
    ) -> None:
        """Send error level log.
        
        Args:
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            exception: Optional exception instance
            **kwargs: Additional log entry fields
        """
        if exception:
            kwargs["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception)
            }
        await self._log("error", message, context, correlation_id, **kwargs)

    async def critical(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        exception: Optional[Exception] = None,
        **kwargs
    ) -> None:
        """Send critical level log.
        
        Args:
            message: Log message
            context: Additional context data
            correlation_id: Optional correlation ID
            exception: Optional exception instance
            **kwargs: Additional log entry fields
        """
        if exception:
            kwargs["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception)
            }
        await self._log("critical", message, context, correlation_id, **kwargs)

    async def batch_log(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send multiple log entries in batch.
        
        Args:
            log_entries: List of log entry data
            
        Raises:
            IntegrationError: If batch logging fails
        """
        prepared_entries = [
            self._prepare_log_entry(**entry)
            for entry in log_entries
            if self.LEVELS[entry.get("level", "info").lower()] >= self.min_level
        ]
        
        if prepared_entries:
            await self._make_request(
                "POST",
                "/logs/batch",
                json={"entries": prepared_entries}
            )

    async def get_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[str] = None,
        service: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve logs with filtering.
        
        Args:
            start_time: Optional start time filter
            end_time: Optional end time filter
            level: Optional log level filter
            service: Optional service name filter
            correlation_id: Optional correlation ID filter
            limit: Maximum number of logs to return
            
        Returns:
            List of matching log entries
            
        Raises:
            IntegrationError: If log retrieval fails
        """
        params = {"limit": limit}
        
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        if level:
            params["level"] = level.upper()
        if service:
            params["service"] = service
        if correlation_id:
            params["correlation_id"] = correlation_id
            
        data = await self._make_request("GET", "/logs", params=params)
        return data.get("logs", [])

    async def healthcheck(self) -> bool:
        """Check Logging service health.
        
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