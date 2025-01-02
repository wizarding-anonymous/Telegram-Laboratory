from fastapi import APIRouter, Depends

from src.api.controllers import HealthController
from src.api.schemas import HealthCheckResponse, ErrorResponse
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
         401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)


@router.get("/", response_model=HealthCheckResponse, dependencies=[Depends(AuthMiddleware())])
async def health_check(controller: HealthController = Depends()) -> HealthCheckResponse:
    """
    Performs a health check of the service and its dependencies.
    """
    return await controller.check_health()