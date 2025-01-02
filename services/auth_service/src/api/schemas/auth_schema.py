from typing import Optional
from pydantic import BaseModel, Field


class AuthRegister(BaseModel):
    """
    Schema for user registration data.
    """
    email: str = Field(..., description="Email address of the new user")
    password: str = Field(..., min_length=6, description="Password for the new user")


class AuthLogin(BaseModel):
    """
    Schema for user login data.
    """
    email: str = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")


class AuthResponse(BaseModel):
    """
    Schema for authentication response, includes JWT access and refresh tokens.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")


class AuthRefresh(BaseModel):
    """
    Schema for refresh token request
    """
    refresh_token: str = Field(..., description="JWT refresh token")