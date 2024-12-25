# services\api_gateway\src\core\metrics_collector.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.db.repositories.metric_repository import MetricRepository
from src.core.exceptions import MetricCollectionError
from src.core.load_balancer import get_load_balancer
from src.core.cache_manager import get_cache_manager

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Collects and aggregates metrics from services."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = MetricRepository(session)
        self._load_balancer = get_load_balancer()
        self._cache_manager = get_cache_manager()

    async def collect_service_metrics(
        self,
        service_name: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Collect metrics for specific service."""
        try:
            service = await self._load_balancer.get_service_instance(service_name)

            metrics = {
                "service_name": service_name,
                "timestamp": timestamp or datetime.utcnow(),
                "response_time": service.last_response_time,
                "requests_count": service.total_requests,
                "error_count": service.failed_requests,
                "success_rate": 100 - service.failure_rate,
                "active_connections": service.active_connections
            }

            await self._repository.create(metrics)
            return metrics

        except Exception as e:
            logger.error(f"Failed to collect metrics for {service_name}: {str(e)}")
            raise MetricCollectionError(f"Metrics collection failed: {str(e)}")

    async def get_aggregated_metrics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated metrics across all services."""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.utcnow()

        services = await self._load_balancer.get_service_stats()
        total_requests = 0
        total_errors = 0
        total_response_time = 0.0
        active_services = 0

        for service_name, stats in services.items():
            metrics = await self._repository.get_service_metrics(
                service_name,
                start_time,
                end_time,
                ["requests_count", "error_count", "response_time"]
            )

            for metric in metrics:
                total_requests += metric.requests_count or 0
                total_errors += metric.error_count or 0
                if metric.response_time:
                    total_response_time += metric.response_time

            if stats.get("status") == "healthy":
                active_services += 1

        return {
            "total_requests": total_requests,
            "error_rate": (total_errors / total_requests * 100) if total_requests else 0,
            "average_response_time": total_response_time / len(metrics) if metrics else 0,
            "active_services": active_services,
            "cache_stats": await self._cache_manager.get_cache_stats(),
            "timestamp": datetime.utcnow()
        }

    async def get_service_metrics(
        self,
        service_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get metrics for specific service."""
        try:
            metrics = await self._repository.get_service_metrics(
                service_name,
                start_time,
                end_time
            )

            if not metrics:
                return {}

            total_requests = sum(m.requests_count or 0 for m in metrics)
            total_errors = sum(m.error_count or 0 for m in metrics)
            total_response_time = sum(m.response_time or 0 for m in metrics if m.response_time)

            return {
                "service_name": service_name,
                "total_requests": total_requests,
                "error_rate": (total_errors / total_requests * 100) if total_requests else 0,
                "average_response_time": total_response_time / len(metrics) if metrics else 0,
                "latest_status": await self._load_balancer.get_service_health(service_name),
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Failed to get metrics for {service_name}: {str(e)}")
            raise MetricCollectionError(f"Failed to get metrics: {str(e)}")

    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get health check metrics for all services."""
        services = await self._load_balancer.get_service_stats()

        health_metrics = {
            name: {
                "status": stats.get("status", "unknown"),
                "last_check": stats.get("last_health_check"),
                "consecutive_failures": stats.get("consecutive_failures", 0),
                "response_time": stats.get("last_response_time", 0)
            }
            for name, stats in services.items()
        }

        return {
            "services": health_metrics,
            "healthy_services": sum(1 for s in health_metrics.values() if s["status"] == "healthy"),
            "total_services": len(health_metrics),
            "timestamp": datetime.utcnow()
        }

    async def cleanup_old_metrics(
        self,
        older_than: datetime
    ) -> int:
        """Delete metrics older than specified time."""
        deleted_count = 0
        services = await self._load_balancer.get_service_stats()

        for service_name in services:
            count = await self._repository.delete_old_metrics(service_name, older_than)
            deleted_count += count

        logger.info(f"Deleted {deleted_count} old metrics entries")
        return deleted_count
