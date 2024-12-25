# services/bot_constructor_service/src/api/routers/health_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.controllers import HealthController  # Импорт через пакет controllers
from src.db.database import get_session
from src.api.schemas.response_schema import HealthCheckResponse, ErrorResponse
from src.integrations import get_current_user  # Обновлённый импорт через integrations/__init__.py

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)


@router.get("/", response_model=HealthCheckResponse)
async def check_health(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),  # Добавлена зависимость current_user
):
    """
    Выполнить проверку состояния сервиса и его зависимостей.

    Этот эндпоинт выполняет проверку доступности баз данных, внешних сервисов и других критически важных компонентов
    системы. Доступ к этому эндпоинту ограничен аутентифицированными пользователями с необходимыми правами.
    """
    controller = HealthController(session)
    return await controller.check_health(current_user)
