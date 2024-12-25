# services\auth_service\src\api\routers\__init__.py
from fastapi import APIRouter
from .auth_router import router as auth_router
from .roles_router import router as roles_router

router = APIRouter()

router.include_router(
   auth_router,
   prefix="/auth",
   tags=["Authentication"]
)

router.include_router(
   roles_router,
   tags=["Roles"]
)

__all__ = ["router"]