from fastapi import APIRouter, Depends

from src.api.controllers import HealthController
from src.api.schemas import HealthCheckResponse, ErrorResponse

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.get("/", response_model=HealthCheckResponse)
async def health_check(controller: HealthController = Depends()) -> HealthCheckResponse:
    """
    Performs a health check of the service and its dependencies.
    """
    return await controller.check_health()