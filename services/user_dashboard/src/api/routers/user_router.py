# services\user_dashboard\src\api\routers\user_router.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserUpdateRequest, UserCreateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user=Depends(get_current_user),
):
    """
    Возвращает профиль текущего пользователя.
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Обновляет профиль текущего пользователя.
    """
    try:
        updated_user = await UserService.update_user(
            db=db, user_id=current_user["id"], user_data=user_data
        )
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Создает нового пользователя (только для администраторов).
    """
    try:
        new_user = await UserService.create_user(db=db, user_data=user_data)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Возвращает список пользователей (только для администраторов).
    """
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        users = await UserService.get_all_users(db=db)
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Удаляет пользователя (только для администраторов).
    """
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        success = await UserService.delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
