# services\auth_service\src\api\schemas\response_schema.py
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    """Base response model for simple messages."""
    message: str
    details: Optional[Dict[str, str]] = None  # Уточнить тип для словаря

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "details": None,
            }
        }

class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str = Field(
        ...,
        description="JWT access token to be used for authenticated requests",
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token to be used for obtaining new access tokens",
    )
    token_type: str = Field(
        default="Bearer",
        description="Type of token, always 'Bearer'",
    )
    expires_in: int = Field(
        ...,
        description="Time in seconds until the access token expires",
    )
    authorization_header: Optional[str] = Field(
        None,
        description="Example of how to use the access token in the Authorization header",
    )
    usage_instructions: Optional[str] = Field(
        None,
        description="Instructions on how to use the tokens",
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.access_token and not self.authorization_header:
            self.authorization_header = f"Bearer {self.access_token}"
        if not self.usage_instructions:
            self.usage_instructions = (
                "To access protected endpoints, add the Authorization header with "
                f"value '{self.authorization_header}' to your requests. "
                "Use the refresh_token to obtain new tokens when the access token expires."
            )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "Bearer",
                "expires_in": 1800,
                "authorization_header": "Bearer eyJhbGciOiJIUzI1NiIs...",
                "usage_instructions": (
                    "To access protected endpoints, add the Authorization header with "
                    "value 'Bearer eyJhbGciOiJIUzI1NiIs...' to your requests. "
                    "Use the refresh_token to obtain new tokens when the access token "
                    "expires."
                ),
            }
        }

class RoleResponse(BaseModel):
    """Response model for user roles."""
    id: int
    name: str
    permissions: List[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "admin",
                "permissions": ["read", "write", "delete"],
            }
        }

class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    email: str
    is_active: bool
    roles: Optional[List[RoleResponse]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "is_active": True,
                "roles": [
                    {
                        "id": 1,
                        "name": "user",
                        "permissions": ["read"],
                    }
                ],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }

class AuthResponse(BaseModel):
    """Comprehensive response model for authentication operations."""
    user: UserResponse = Field(
        ...,
        description="User information",
    )
    tokens: TokenResponse = Field(
        ...,
        description="Authentication tokens and usage instructions",
    )
    message: str = Field(
        default=(
            "Authentication successful. Please check tokens.usage_instructions "
            "for details on how to use the tokens."
        ),
        description="Informative message about the authentication status",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "is_active": True,
                    "roles": [
                        {
                            "id": 1,
                            "name": "user",
                            "permissions": ["read"],
                        }
                    ],
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                    "token_type": "Bearer",
                    "expires_in": 1800,
                    "authorization_header": "Bearer eyJhbGciOiJIUzI1NiIs...",
                    "usage_instructions": (
                        "To access protected endpoints, add the Authorization header "
                        "with value 'Bearer eyJhbGciOiJIUzI1NiIs...' to your requests. "
                        "Use the refresh_token to obtain new tokens when the access "
                        "token expires."
                    ),
                },
                "message": (
                    "Authentication successful. Please check tokens.usage_instructions "
                    "for details on how to use the tokens."
                ),
            }
        }

class TokenVerificationResponse(BaseModel):
    """Response model for token verification."""
    is_valid: bool = Field(
        ...,
        description="Indicates if the token is valid",
    )
    user_id: Optional[int] = Field(
        None,
        description="ID of the user if token is valid",
    )
    expires_in: Optional[int] = Field(
        None,
        description="Seconds until token expiration if valid",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "user_id": 1,
                "expires_in": 1700,
            }
        }