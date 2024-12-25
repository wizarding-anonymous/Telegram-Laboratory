# services\api_gateway\src\api\routers\health_router.py
from fastapi import APIRouter, Depends, status
from typing import Dict, List

from src.api.dependencies.service_provider import get_service_provider
from src.core.interfaces.service_provider import ServiceProvider
from src.core.schemas.health import (
    HealthResponse,
    ServiceHealth,
    ServiceStatus,
    DetailedHealthResponse
)

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get API Gateway health status"
)
async def get_health() -> HealthResponse:
    """
    Get the current health status of the API Gateway service.
    
    Returns:
        HealthResponse: Basic health status of the API Gateway
    """
    return HealthResponse(
        service="api_gateway",
        status=ServiceStatus.HEALTHY,
        version="1.0.0"  # This should be pulled from your config or environment
    )


@router.get(
    "/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed health status of all services"
)
async def get_detailed_health(
    service_provider: ServiceProvider = Depends(get_service_provider)
) -> DetailedHealthResponse:
    """
    Get detailed health status of the API Gateway and all connected microservices.
    
    Args:
        service_provider: Dependency injection of ServiceProvider
        
    Returns:
        DetailedHealthResponse: Detailed health status of all services
    """
    # Check health of all registered services
    service_statuses: List[ServiceHealth] = []
    
    # Add API Gateway status
    service_statuses.append(
        ServiceHealth(
            service="api_gateway",
            status=ServiceStatus.HEALTHY,
            version="1.0.0",
            details={
                "uptime": "TODO: Add uptime logic",
                "memory_usage": "TODO: Add memory usage logic"
            }
        )
    )
    
    # Check each microservice health
    for service_name, service_client in service_provider.get_all_services().items():
        try:
            # Attempt to get health status from each service
            service_health = await service_client.get_health()
            service_statuses.append(service_health)
        except Exception as e:
            # If service is unreachable or returns error, mark as unhealthy
            service_statuses.append(
                ServiceHealth(
                    service=service_name,
                    status=ServiceStatus.UNHEALTHY,
                    version="unknown",
                    details={
                        "error": str(e),
                        "message": f"Failed to connect to {service_name} service"
                    }
                )
            )
    
    return DetailedHealthResponse(
        timestamp=datetime.datetime.utcnow(),
        services=service_statuses
    )


@router.get(
    "/{service_name}",
    response_model=ServiceHealth,
    status_code=status.HTTP_200_OK,
    summary="Get health status of specific service"
)
async def get_service_health(
    service_name: str,
    service_provider: ServiceProvider = Depends(get_service_provider)
) -> ServiceHealth:
    """
    Get health status of a specific microservice.
    
    Args:
        service_name: Name of the service to check
        service_provider: Dependency injection of ServiceProvider
        
    Returns:
        ServiceHealth: Health status of the specified service
        
    Raises:
        HTTPException: If service is not found or unreachable
    """
    try:
        if service_name == "api_gateway":
            return ServiceHealth(
                service="api_gateway",
                status=ServiceStatus.HEALTHY,
                version="1.0.0",
                details={
                    "uptime": "TODO: Add uptime logic",
                    "memory_usage": "TODO: Add memory usage logic"
                }
            )
            
        service_client = service_provider.get_service(service_name)
        return await service_client.get_health()
        
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found"
        )
    except Exception as e:
        # If service is unreachable, return unhealthy status
        return ServiceHealth(
            service=service_name,
            status=ServiceStatus.UNHEALTHY,
            version="unknown",
            details={
                "error": str(e),
                "message": f"Failed to connect to {service_name} service"
            }
        )