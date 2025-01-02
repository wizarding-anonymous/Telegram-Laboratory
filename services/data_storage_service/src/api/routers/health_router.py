from fastapi import APIRouter, Depends

from src.api.controllers import HealthController
from src.api.schemas import HealthCheckResponse


router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthCheckResponse,
)
async def health_check(controller: HealthController = Depends()) -> HealthCheckResponse:
    """
    Performs a health check for the service.
    """
    return await controller.health_check()