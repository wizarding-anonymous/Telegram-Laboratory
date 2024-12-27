# user_dashboard/src/api/controllers/user_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from user_dashboard.src.schemas.user_schema import (
    UserProfileResponse,
    UserProfileUpdate,
    PasswordResetRequest,
    PasswordChangeRequest,
)
from user_dashboard.src.models.user_model import User
from user_dashboard.src.core.auth import get_current_user, verify_password, hash_password
from user_dashboard.src.core.user_service import (
    get_user_profile,
    update_user_profile,
    initiate_password_reset,
    change_user_password,
)
from user_dashboard.src.db.database import get_db
from user_dashboard.src.integrations.logging_client import log_event

router = APIRouter(
    prefix="/user",
    tags=["User Management"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/profile", response_model=UserProfileResponse)
async def read_user_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Any:
    """
    Получение профиля текущего пользователя.
    """
    try:
        profile = await get_user_profile(db, current_user.id)
        await log_event(db, "INFO", f"User {current_user.email} accessed their profile.")
        return profile
    except Exception as e:
        await log_event(db, "ERROR", f"Error fetching profile for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Обновление профиля текущего пользователя.
    """
    try:
        updated_profile = await update_user_profile(db, current_user.id, profile_update)
        await log_event(db, "INFO", f"User {current_user.email} updated their profile.")
        return updated_profile
    except Exception as e:
        await log_event(db, "ERROR", f"Error updating profile for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/password/reset", response_model=dict)
async def reset_password(
    password_reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Запрос на сброс пароля. Отправляет email с инструкциями по сбросу.
    """
    try:
        await initiate_password_reset(db, password_reset_request.email)
        await log_event(db, "INFO", f"Password reset requested for email {password_reset_request.email}.")
        return {"message": "Password reset email sent"}
    except ValueError as ve:
        await log_event(db, "WARNING", f"Password reset failed for email {password_reset_request.email}: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        await log_event(db, "ERROR", f"Error initiating password reset for email {password_reset_request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/password/change", response_model=dict)
async def change_password(
    password_change_request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Изменение пароля текущего пользователя.
    """
    try:
        if not verify_password(password_change_request.old_password, current_user.hashed_password):
            await log_event(db, "WARNING", f"User {current_user.email} provided incorrect old password.")
            raise HTTPException(status_code=400, detail="Incorrect old password")
        
        new_hashed_password = hash_password(password_change_request.new_password)
        await change_user_password(db, current_user.id, new_hashed_password)
        await log_event(db, "INFO", f"User {current_user.email} changed their password.")
        return {"message": "Password changed successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        await log_event(db, "ERROR", f"Error changing password for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
