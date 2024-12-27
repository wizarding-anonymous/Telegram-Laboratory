# services\user_dashboard\src\api\controllers\user_controller.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_user
from services.user_service import UserService

router = APIRouter()

# Pydantic модели
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

class UserUpdateRequest(BaseModel):
    full_name: str
    password: str

class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str


# Эндпоинты
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(user=Depends(get_current_user)):
    """
    Получение профиля текущего пользователя.
    """
    return user


@router.put("/users/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Обновление профиля текущего пользователя.
    """
    try:
        updated_user = await UserService.update_user(
            db=db,
            user_id=user.id,
            full_name=user_data.full_name,
            password=user_data.password,
        )
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Создание нового пользователя (для администраторов).
    """
    try:
        new_user = await UserService.create_user(
            db=db,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
        )
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Получение списка всех пользователей (только для администраторов).
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        users = await UserService.get_all_users(db=db)
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Получение информации о пользователе по ID (для администраторов).
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        user_data = await UserService.get_user_by_id(db=db, user_id=user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Удаление пользователя (только для администраторов).
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden")
    try:
        success = await UserService.delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
