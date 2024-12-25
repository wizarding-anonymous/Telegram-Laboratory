# services/auth_service/src/api/controllers/auth_controller.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.api.schemas.request_schema import UserRegisterRequest, UserLoginRequest, BulkRoleUpdateRequest
from src.api.schemas.response_schema import TokenResponse, UserResponse, AuthResponse
from src.db.repositories.user_repository import (
    UserRepository,
    UserRepositoryError, 
    UserNotFoundError,
    UserCreationError,
    UserUpdateError,
    UserDeletionError,
    RoleAssignmentError
)
from src.db.repositories.session_repository import (
    SessionRepository,
    SessionCreationError,
    SessionDeletionError
)
from src.db.repositories.role_repository import (
    RoleRepository, 
    RoleNotFoundError,
    RoleCreationError, 
    RoleUpdateError,
    RoleDeletionError,
    RoleRepositoryError
)
from src.core.utils.security import (
    verify_password,
    get_password_hash,
    create_jwt_tokens, 
    verify_and_decode_token,
    get_token_expiration, 
    RoleType,
    get_default_role_permissions
)
from loguru import logger
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
import pytz


class AuthController:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)
        self.role_repo = RoleRepository(session)

    async def ensure_default_roles(self) -> None:
        try:
            logger.debug("Ensuring default roles exist...")
            
            roles = await self.role_repo.get_all_roles()
            existing_roles = {role.name for role in roles}
            
            for role_type in RoleType:
                if role_type.value not in existing_roles:
                    permissions = get_default_role_permissions(role_type.value)
                    await self.role_repo.create_role(role_type.value, permissions)
                    logger.info(f"Created default role: {role_type.value}")
            
            logger.info("Default roles verified successfully")
        except Exception as e:
            logger.error(f"Failed to ensure default roles: {str(e)}")
            raise

    async def _assign_default_roles(self, user_id: int, is_admin: bool = False) -> None:
        try:
            user_role = await self.role_repo.get_by_name(RoleType.USER.value)
            if not user_role:
                raise RoleNotFoundError("Default USER role not found")
            await self.user_repo.assign_role_to_user(user_id, user_role.id)
            
            if is_admin:
                admin_role = await self.role_repo.get_by_name(RoleType.ADMIN.value)
                if not admin_role:
                    raise RoleNotFoundError("Default ADMIN role not found")
                await self.user_repo.assign_role_to_user(user_id, admin_role.id)
            
            logger.info(f"Successfully assigned default roles to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to assign default roles: {str(e)}")
            raise

    async def register_user(
        self, 
        user_data: UserRegisterRequest
    ) -> Tuple[UserResponse, Dict[str, Any]]:
        try:
            logger.debug(f"Starting registration for email: {user_data.email}")
            
            existing = await self.user_repo.get_by_email(user_data.email)
            if existing:
                logger.warning(f"User with email {user_data.email} already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )

            await self.ensure_default_roles()

            hashed_pw = get_password_hash(user_data.password)
            created_user = await self.user_repo.create_user(user_data.email, hashed_pw)

            is_admin = user_data.email.endswith("@admin.com")
            await self._assign_default_roles(created_user.id, is_admin)

            loaded_user = await self.user_repo.get_by_id(created_user.id)
            
            additional_claims = await self._get_token_claims(loaded_user)
            tokens = create_jwt_tokens(loaded_user.id, additional_claims)

            await self.session_repo.create_session(
                user_id=loaded_user.id,
                refresh_token=tokens["refresh_token"]
            )

            logger.info(f"Successfully registered user: {user_data.email}")
            return UserResponse.from_orm(loaded_user), tokens

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration failed for {user_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )

    async def login_user(
        self, 
        user_data: UserLoginRequest
    ) -> Tuple[UserResponse, Dict[str, Any]]:
        try:
            logger.debug(f"Login attempt for email: {user_data.email}")
            
            user = await self.user_repo.get_by_email(user_data.email)
            if not user or not verify_password(user_data.password, user.hashed_password):
                logger.warning(f"Invalid login attempt for {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            if not user.is_active:
                logger.warning(f"Login attempt for deactivated account: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )

            if not user.roles:
                logger.warning(f"User {user_data.email} has no roles, assigning defaults")
                await self._assign_default_roles(user.id)
                user = await self.user_repo.get_by_id(user.id)

            additional_claims = await self._get_token_claims(user)
            tokens = create_jwt_tokens(user.id, additional_claims)

            await self.session_repo.create_session(
                user_id=user.id,
                refresh_token=tokens["refresh_token"]
            )

            logger.info(f"Successfully logged in user: {user_data.email}")
            return UserResponse.from_orm(user), tokens

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed for {user_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )

    async def logout_user(self, refresh_token: str, authorization: Optional[str] = None) -> None:
        try:
            logger.debug("Starting logout process")
            
            if authorization:
                access_token = authorization.replace("Bearer ", "")
                payload, is_valid = verify_and_decode_token(access_token, expected_type="access")
                if not is_valid:
                    logger.warning("Invalid access token during logout")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid access token"
                    )

            payload, is_valid = verify_and_decode_token(refresh_token, expected_type="refresh")
            if not is_valid:
                logger.warning("Invalid refresh token during logout")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            deleted = await self.session_repo.delete_session_by_token(refresh_token)
            if not deleted:
                logger.warning("No session found for given refresh token")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )

            logger.info(f"Successfully logged out user: {payload.get('sub')}")

        except HTTPException:
            raise
        except SessionDeletionError as se:
            logger.error(f"Session deletion error during logout: {str(se)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed due to session error"
            )
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        try:
            logger.debug("Starting token refresh")
            
            payload, is_valid = verify_and_decode_token(refresh_token, expected_type="refresh")
            if not is_valid:
                logger.warning("Invalid refresh token during refresh process")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            user_id = payload.get("sub")
            if not user_id:
                logger.error("Token missing user ID")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )

            user = await self.user_repo.get_by_id(int(user_id))
            if not user or not user.is_active:
                logger.warning(f"Inactive or non-existent user during refresh: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )

            if not user.roles:
                logger.warning(f"User {user_id} has no roles during token refresh")
                await self._assign_default_roles(user.id)
                user = await self.user_repo.get_by_id(user.id)

            deleted = await self.session_repo.delete_session_by_token(refresh_token)
            if not deleted:
                logger.warning("No session found for given refresh token during refresh")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )

            additional_claims = await self._get_token_claims(user)
            tokens = create_jwt_tokens(user.id, additional_claims)

            await self.session_repo.create_session(
                user_id=user.id,
                refresh_token=tokens["refresh_token"]
            )

            logger.info(f"Successfully refreshed tokens for user: {user_id}")
            return TokenResponse(**tokens)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )
            
    async def bulk_update_user_roles(self, bulk_data: BulkRoleUpdateRequest) -> None:
        try:
            logger.debug(f"Bulk updating roles for {len(bulk_data.user_ids)} users")
            
            await self.user_repo.bulk_update_user_roles(bulk_data.user_ids, bulk_data.role_ids)
            
            logger.info(f"Successfully updated roles for {len(bulk_data.user_ids)} users")
        except HTTPException:
            raise  
        except Exception as e:
            logger.error(f"Bulk role update failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bulk role update failed"
            )

    async def _get_token_claims(self, user: Any) -> Dict[str, Any]:
        try:
            roles = [role.name for role in user.roles] if user.roles else []
            
            permissions = set()
            for role in (user.roles or []):
                if isinstance(role.permissions, (list, set)):
                    permissions.update(role.permissions)
                elif isinstance(role.permissions, dict):
                    permissions.update(role.permissions.values())

            current_time_utc = datetime.now(pytz.utc).isoformat()
            
            claims = {
                "sub": str(user.id),
                "email": user.email,
                "roles": sorted(list(roles)),
                "permissions": sorted(list(permissions)),
                "is_active": user.is_active,
                "last_login": current_time_utc
            }
            
            logger.debug(f"Generated token claims for user {user.id}: {claims}")
            return claims
            
        except Exception as e:
            logger.error(f"Error generating token claims: {str(e)}")
            raise