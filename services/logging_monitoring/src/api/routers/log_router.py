from fastapi import APIRouter, Depends, status, Query
from typing import Optional

from src.api.controllers import LogController
from src.api.schemas import (
    LogCreate,
    LogResponse,
    LogListResponse,
    SuccessResponse,
    ErrorResponse,
)
from src.api.middleware.auth import AuthMiddleware, admin_required

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)


@router.post(
    "/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new log entry",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def create_log(
    log_data: LogCreate, controller: LogController = Depends()
) -> SuccessResponse:
    """
    Creates a new log entry.
    """
    return await controller.create_log(log_data=log_data)


@router.get(
    "/",
    response_model=LogListResponse,
    summary="Get a list of all logs with optional filters",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def get_logs(
    controller: LogController = Depends(),
    level: Optional[str] = Query(None, description="Filter logs by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    service: Optional[str] = Query(None, description="Filter logs by service name"),
    start_time: Optional[str] = Query(None, description="Filter logs by start time"),
    end_time: Optional[str] = Query(None, description="Filter logs by end time"),
) -> LogListResponse:
    """
    Retrieves a list of logs, supporting filters for level, service, start_time, and end_time.
    """
    return await controller.get_logs(level=level, service=service, start_time=start_time, end_time=end_time)

@router.get(
    "/all",
    response_model=LogListResponse,
    summary="Get a list of all logs",
    dependencies=[Depends(AuthMiddleware()), Depends(admin_required())]
)
async def get_all_logs(controller: LogController = Depends()) -> LogListResponse:
     """
    Retrieves all logs.
    """
     return await controller.get_all_logs()