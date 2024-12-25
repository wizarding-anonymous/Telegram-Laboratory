# services\api_gateway\src\api\routers\health_router.py
from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.core.di.containers import Container
from src.core.services.health_service import HealthService
from dependency_injector.wiring import inject, Provide

router = APIRouter(
    prefix="/health",
    tags=["Health Check"],
)

@router.get(
    "",
    summary="Health check endpoint",
    description="Returns the health status of the service and its dependencies",
    response_description="Health check information",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "dependencies": {
                            "auth_service": "healthy",
                            "user_service": "healthy"
                        }
                    }
                }
            }
        },
        503: {
            "description": "Service is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "version": "1.0.0",
                        "dependencies": {
                            "auth_service": "unhealthy",
                            "user_service": "healthy"
                        }
                    }
                }
            }
        }
    }
)
@inject
async def check_health(
    health_service: HealthService = Depends(Provide[Container.health_service])
) -> JSONResponse:
    """
    Проверяет состояние здоровья сервиса и его зависимостей.
    
    Returns:
        JSONResponse: Ответ с информацией о состоянии здоровья сервиса и его зависимостей.
            - status (str): Общий статус здоровья сервиса ("healthy" или "unhealthy")
            - version (str): Версия сервиса
            - dependencies (Dict): Статусы здоровья зависимых сервисов
    """
    health_info: Dict = await health_service.check_health()
    
    # Определяем HTTP статус на основе общего состояния здоровья
    http_status = 200 if health_info["status"] == "healthy" else 503
    
    return JSONResponse(
        status_code=http_status,
        content=health_info
    )