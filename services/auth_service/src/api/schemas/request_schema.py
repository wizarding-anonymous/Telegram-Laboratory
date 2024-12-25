# services\auth_service\src\api\schemas\request_schema.py

from pydantic import BaseModel, EmailStr, Field, constr
from typing import List, Optional


class UserRegisterRequest(BaseModel):
    """
    Схема для регистрации нового пользователя.
    """
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )
    password: constr(min_length=8, max_length=100) = Field(
        ...,
        description="Пароль пользователя (минимум 8 символов)",
        example="SecurePassword123"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123"
            }
        }


class UserLoginRequest(BaseModel):
    """
    Схема для входа пользователя.
    """
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )
    password: constr(min_length=1) = Field(
        ...,
        description="Пароль пользователя",
        example="SecurePassword123"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123"
            }
        }


class LogoutRequest(BaseModel):
    """
    Схема для выхода пользователя.
    """
    refresh_token: constr(min_length=1) = Field(
        ...,
        description="Refresh токен для выхода",
        example="eyJhbGciOiJIUzI1NiIs..."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }


class RoleCreateRequest(BaseModel):
    """
    Схема для создания новой роли.
    """
    name: constr(min_length=1, max_length=255) = Field(
        ...,
        description="Название роли",
        example="admin"
    )
    permissions: List[str] = Field(
        ...,
        description="Список разрешений для роли",
        example=["read", "write", "delete"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "admin",
                "permissions": ["read", "write", "delete"]
            }
        }


class RoleUpdateRequest(BaseModel):
    """
    Схема для обновления роли.
    """
    name: Optional[constr(min_length=1, max_length=255)] = Field(
        None,
        description="Новое название роли",
        example="editor"
    )
    permissions: Optional[List[str]] = Field(
        None,
        description="Новый список разрешений",
        example=["read", "write"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "editor",
                "permissions": ["read", "write"]
            }
        }


class AssignRoleRequest(BaseModel):
    """
    Схема для назначения роли пользователю.
    """
    user_id: int = Field(
        ...,
        description="ID пользователя",
        gt=0,
        example=1
    )
    role_id: int = Field(
        ...,
        description="ID роли",
        gt=0,
        example=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "role_id": 1
            }
        }


class TokenRefreshRequest(BaseModel):
    """
    Схема для обновления токена доступа.
    """
    refresh_token: constr(min_length=1) = Field(
        ...,
        description="Refresh токен для получения нового access токена",
        example="eyJhbGciOiJIUzI1NiIs..."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }


class PasswordResetRequest(BaseModel):
    """
    Схема для сброса пароля.
    """
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordChangeRequest(BaseModel):
    """
    Схема для изменения пароля.
    """
    current_password: constr(min_length=1) = Field(
        ...,
        description="Текущий пароль",
        example="CurrentPassword123"
    )
    new_password: constr(min_length=8, max_length=100) = Field(
        ...,
        description="Новый пароль (минимум 8 символов)",
        example="NewSecurePassword123"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "CurrentPassword123",
                "new_password": "NewSecurePassword123"
            }
        }