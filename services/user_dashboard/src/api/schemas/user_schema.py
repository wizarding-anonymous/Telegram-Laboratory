# services\user_dashboard\src\api\schemas\user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Базовая модель пользователя.
    """
    email: EmailStr = Field(..., title="Email", description="Электронная почта пользователя")
    full_name: Optional[str] = Field(None, title="Full Name", description="Полное имя пользователя")
    is_active: Optional[bool] = Field(True, title="Active Status", description="Статус активности пользователя")


class UserCreateRequest(UserBase):
    """
    Модель для создания нового пользователя.
    """
    password: str = Field(..., title="Password", description="Пароль пользователя")


class UserUpdateRequest(BaseModel):
    """
    Модель для обновления данных пользователя.
    """
    full_name: Optional[str] = Field(None, title="Full Name", description="Полное имя пользователя")
    password: Optional[str] = Field(None, title="Password", description="Пароль пользователя")


class UserResponse(UserBase):
    """
    Модель ответа для отображения данных пользователя.
    """
    id: int = Field(..., title="User ID", description="Уникальный идентификатор пользователя")
    created_at: datetime = Field(..., title="Created At", description="Дата и время создания")
    updated_at: datetime = Field(..., title="Updated At", description="Дата и время последнего обновления")

    class Config:
        orm_mode = True
