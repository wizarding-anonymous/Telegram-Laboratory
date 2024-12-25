# services/auth_service/src/core/utils/security.py
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple, Union, List
from src.config import settings
from loguru import logger
from fastapi import HTTPException, status
from enum import Enum

# Определяем часовой пояс по умолчанию
DEFAULT_TIMEZONE = timezone.utc

# Определяем базовые роли и разрешения
class RoleType(str, Enum):
    ADMIN = "admin"
    USER = "user"

class PermissionType(str, Enum):
    # User management
    READ_USERS = "read:users"
    CREATE_USERS = "create:users"
    UPDATE_USERS = "update:users"
    DELETE_USERS = "delete:users"
    
    # Role management
    READ_ROLES = "read:roles"
    CREATE_ROLES = "create:roles"
    UPDATE_ROLES = "update:roles"
    DELETE_ROLES = "delete:roles"
    
    # Bot management
    READ_BOTS = "read:bots"
    CREATE_BOTS = "create:bots"
    UPDATE_BOTS = "update:bots"
    DELETE_BOTS = "delete:bots"
    
    # Session management
    READ_SESSIONS = "read:sessions"
    DELETE_SESSIONS = "delete:sessions"

# Определяем разрешения для базовых ролей
DEFAULT_ROLE_PERMISSIONS = {
    RoleType.ADMIN: [perm.value for perm in PermissionType],  # Все разрешения
    RoleType.USER: [
        PermissionType.READ_BOTS.value,
        PermissionType.CREATE_BOTS.value,
        PermissionType.UPDATE_BOTS.value,
        PermissionType.DELETE_BOTS.value,
        PermissionType.READ_SESSIONS.value,
        PermissionType.DELETE_SESSIONS.value
    ]
}

def get_default_role_permissions(role_name: str) -> List[str]:
    """
    Получает список разрешений для базовой роли.
    
    Args:
        role_name: Название роли
        
    Returns:
        List[str]: Список разрешений
    """
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])

def get_password_hash(password: str) -> str:
    """
    Generates a hash for the given password using bcrypt.
    """
    logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error(f"Password hashing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain password matches a hashed password.
    """
    logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")
    if not plain_password or not hashed_password:
        raise ValueError("Both passwords must be non-empty")

    try:
        is_valid = bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
        logger.debug(f"Password verification result: {is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"Password verification failed: {str(e)}")
        return False

def create_jwt_tokens(
    user_id: int,
    additional_claims: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, int]]:
    """
    Creates a pair of JWT tokens (access and refresh) for a user.
    """
    logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")
    if not isinstance(user_id, int) or user_id < 1:
        raise ValueError("Invalid user_id")

    try:
        current_time = datetime.now(DEFAULT_TIMEZONE)

        base_claims = {
            "sub": str(user_id),
            "iat": int(current_time.timestamp()),
            **(additional_claims or {})
        }

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token_exp = current_time + access_token_expires
        refresh_token_exp = current_time + refresh_token_expires

        logger.debug(f"Access token expiration time: {access_token_exp} (UTC)")
        logger.debug(f"Refresh token expiration time: {refresh_token_exp} (UTC)")

        access_token_data = {
            **base_claims,
            "type": "access",
            "exp": int(access_token_exp.timestamp()),
            "nbf": int(current_time.timestamp())
        }

        refresh_token_data = {
            **base_claims,
            "type": "refresh",
            "exp": int(refresh_token_exp.timestamp()),
            "nbf": int(current_time.timestamp())
        }

        access_token = _create_token(access_token_data)
        refresh_token = _create_token(refresh_token_data)

        logger.debug(f"Created token pair for user_id: {user_id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }

    except Exception as e:
        logger.error(f"Failed to create tokens for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating authentication tokens"
        )

def _create_token(payload: Dict[str, Any]) -> str:
    """
    Creates a JWT token with the specified payload.
    """
    logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")
    try:
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return token
    except Exception as e:
        logger.error(f"Token creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating token"
        )

def verify_and_decode_token(
    token: str,
    expected_type: Optional[str] = None
) -> Tuple[Dict[str, Any], bool]:
    """
    Verifies and decodes a JWT token.
    """
    logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")
    try:
        if not token:
            logger.error("Empty token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )

        leeway = timedelta(minutes=1)

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            leeway=int(leeway.total_seconds())
        )

        logger.debug(f"Decoded token payload: {payload}")
        logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")

        if expected_type and payload.get("type") != expected_type:
            logger.warning("Token type mismatch")
            return payload, False

        if not payload.get("sub"):
            logger.error("Token missing user ID")
            return payload, False

        logger.debug(
            f"Token verification successful for user_id: {payload.get('sub')}"
        )

        return payload, True

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

def get_token_expiration(token: str) -> Optional[int]:
    """
    Retrieves the remaining time until token expiration in seconds.
    """
    logger.debug(f"Current time: {datetime.now(DEFAULT_TIMEZONE)}")
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        exp = payload.get("exp")
        if not exp:
            logger.warning("Token does not contain expiration time")
            return None

        now = datetime.now(DEFAULT_TIMEZONE)
        exp_datetime = datetime.fromtimestamp(exp, DEFAULT_TIMEZONE)
        remaining = (exp_datetime - now).total_seconds()

        logger.debug(f"Token expiration remaining time: {remaining} seconds")

        return max(int(remaining), 0)
    except Exception as e:
        logger.warning(f"Failed to calculate token expiration: {str(e)}")
        return None