# services\auth_service\src\api\routers\admin_router.py
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from src.api.schemas.response_schema import MessageResponse
from src.api.middleware.auth_middleware import admin_required

router = APIRouter(tags=["Admin"])

@router.get("/admin-only", response_model=MessageResponse, dependencies=[Depends(admin_required())])
async def admin_only_endpoint():
    """
    Пример эндпоинта, доступного только администраторам.
    """
    return MessageResponse(message="Welcome, admin!")