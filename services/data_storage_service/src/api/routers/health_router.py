# services\data_storage_service\src\api\routers\health_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers.health_controller import HealthController
from src.api.schemas.response_schema import HealthCheckResponse
from src.db.database import get_session

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)


@router.get(
    "/",
    response_model=HealthCheckResponse,
    summary="Check service health",
    description="Performs health check of the microservice and its dependencies",
)
async def check_health(session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для выполнения проверки состояния микросервиса и его зависимостей.

    Проверяется:
    - Подключение к базе данных
    - Доступность Telegram API
    - Доступность Auth Service
    - Состояние миграций для базы данных бота

    Returns:
        HealthCheckResponse: Объект, содержащий:
            - status (str): Статус сервиса ('healthy', 'degraded', 'unhealthy')
            - details (Dict): Подробная информация о состоянии каждой зависимости
            - version (str): Версия микросервиса
            - migrations (Optional[str]): Статус миграций баз данных
    
    Raises:
        HTTPException: В случае серьезных проблем с сервисом или его зависимостями
    """
    try:
        controller = HealthController(session)
        health_status = await controller.check_health()
        return HealthCheckResponse(
            status=health_status["status"],
            details=health_status["details"],
            version=health_status["version"],
            migrations=health_status.get("migrations")
        )
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            details={
                "error": {
                    "status": "unhealthy",
                    "message": f"Service health check failed: {str(e)}"
                }
            },
            version="1.0.0",
            migrations="unknown"
        )


@router.get(
    "/readiness",
    response_model=HealthCheckResponse,
    summary="Check service readiness",
    description="Performs readiness check of the microservice",
)
async def check_readiness(session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для проверки готовности сервиса к обработке запросов.

    Проверяется:
    - Подключение к базе данных
    - Статус миграций
    - Основные зависимости

    Returns:
        HealthCheckResponse: Объект, содержащий информацию о готовности сервиса
    """
    try:
        controller = HealthController(session)
        readiness_status = await controller.check_readiness()
        return HealthCheckResponse(
            status=readiness_status["status"],
            details=readiness_status["details"],
            version=readiness_status["version"],
            migrations=readiness_status.get("migrations")
        )
    except Exception as e:
        logger.error(f"Error during readiness check: {str(e)}")
        return HealthCheckResponse(
            status="not_ready",
            details={
                "error": {
                    "status": "unhealthy",
                    "message": f"Service is not ready: {str(e)}"
                }
            },
            version="1.0.0",
            migrations="unknown"
        )


@router.get(
    "/liveness",
    response_model=HealthCheckResponse,
    summary="Check service liveness",
    description="Performs basic liveness check of the microservice",
)
async def check_liveness():
    """
    Эндпоинт для базовой проверки работоспособности сервиса.
    
    Этот эндпоинт не выполняет сложных проверок и предназначен
    для быстрого определения, что сервис запущен и отвечает на запросы.

    Returns:
        HealthCheckResponse: Объект, содержащий базовую информацию о работоспособности
    """
    return HealthCheckResponse(
        status="healthy",
        details={
            "service": {
                "status": "healthy",
                "message": "Service is alive"
            }
        },
        version="1.0.0"
    )