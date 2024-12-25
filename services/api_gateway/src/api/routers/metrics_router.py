# services/api_gateway/src/api/routers/metrics_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta
from loguru import logger

from src.api.dependencies import get_current_user
from src.api.schemas.response_schema import (
    MetricsResponse,
    ErrorResponse,
    ServiceMetricsResponse
)
from src.api.middleware.auth_middleware import check_permissions
from src.core.metrics_collector import MetricsCollector
from src.db.database import get_session
from src.integrations.auth_service import AuthService
from src.integrations.monitoring_service import MonitoringService
from src.core.utils.validators import validate_timerange

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
    responses={
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

@router.get(
    "/",
    response_model=MetricsResponse,
    description="Get aggregated metrics for all microservices",
    dependencies=[Depends(check_permissions(["view_metrics"]))]
)
async def get_metrics(
    start_time: datetime = None,
    end_time: datetime = None,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> MetricsResponse:
    """
    Get aggregated metrics across all microservices.
    
    Args:
        start_time (datetime): Start of the time range for metrics
        end_time (datetime): End of the time range for metrics
        user (dict): Current user information
        session (AsyncSession): Database session
        
    Returns:
        MetricsResponse: Aggregated metrics data
    """
    try:
        if start_time and end_time:
            validate_timerange(start_time, end_time)
            
        metrics_collector = MetricsCollector(session)
        monitoring_service = MonitoringService()
        
        # Get metrics from all services
        metrics = await metrics_collector.get_aggregated_metrics(
            start_time=start_time,
            end_time=end_time
        )
        
        # Get system metrics
        system_metrics = await monitoring_service.get_system_metrics()
        
        return MetricsResponse(
            total_requests=metrics.get("total_requests", 0),
            average_response_time=metrics.get("average_response_time", 0),
            error_rate=metrics.get("error_rate", 0),
            total_active_users=metrics.get("total_active_users", 0),
            cpu_usage=system_metrics.get("cpu_usage", 0),
            memory_usage=system_metrics.get("memory_usage", 0),
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve metrics"
        )

@router.get(
    "/service/{service_name}",
    response_model=ServiceMetricsResponse,
    description="Get metrics for a specific microservice",
    dependencies=[Depends(check_permissions(["view_metrics"]))]
)
async def get_service_metrics(
    service_name: str,
    start_time: datetime = None,
    end_time: datetime = None,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> ServiceMetricsResponse:
    """
    Get metrics for a specific microservice.
    
    Args:
        service_name (str): Name of the microservice
        start_time (datetime): Start of the time range for metrics
        end_time (datetime): End of the time range for metrics
        user (dict): Current user information
        session (AsyncSession): Database session
        
    Returns:
        ServiceMetricsResponse: Service-specific metrics
    """
    try:
        if start_time and end_time:
            validate_timerange(start_time, end_time)
            
        metrics_collector = MetricsCollector(session)
        
        # Get service-specific metrics
        metrics = await metrics_collector.get_service_metrics(
            service_name=service_name,
            start_time=start_time,
            end_time=end_time
        )
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for service: {service_name}"
            )
            
        return ServiceMetricsResponse(
            service_name=service_name,
            requests_count=metrics.get("requests_count", 0),
            average_response_time=metrics.get("average_response_time", 0),
            error_count=metrics.get("error_count", 0),
            success_rate=metrics.get("success_rate", 0),
            active_connections=metrics.get("active_connections", 0),
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics for service: {service_name}"
        )

@router.get(
    "/health",
    description="Get health metrics for all services",
    dependencies=[Depends(check_permissions(["view_metrics"]))]
)
async def get_health_metrics(
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get health status metrics for all microservices.
    
    Args:
        user (dict): Current user information
        session (AsyncSession): Database session
        
    Returns:
        Dict[str, Any]: Health status information for all services
    """
    try:
        metrics_collector = MetricsCollector(session)
        monitoring_service = MonitoringService()
        
        # Get health status from all services
        health_metrics = await metrics_collector.get_health_metrics()
        
        # Get system health
        system_health = await monitoring_service.get_system_health()
        
        return {
            "services": health_metrics,
            "system": system_health,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting health metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve health metrics"
        )

@router.get(
    "/alerts",
    description="Get active alerts and warnings",
    dependencies=[Depends(check_permissions(["view_metrics"]))]
)
async def get_alerts(
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Get list of active alerts and warnings from monitoring.
    
    Args:
        user (dict): Current user information
        session (AsyncSession): Database session
        
    Returns:
        List[Dict[str, Any]]: List of active alerts
    """
    try:
        monitoring_service = MonitoringService()
        alerts = await monitoring_service.get_active_alerts()
        
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve alerts"
        )