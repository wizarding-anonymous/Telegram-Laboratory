from typing import Dict, Optional
from datetime import timedelta, datetime
import jwt
from fastapi import HTTPException, Depends, status
from loguru import logger
from passlib.context import CryptContext

from src.config import settings
from src.core.utils import handle_exceptions
from src.db.repositories import UserRepository, SessionRepository
from src.integrations.logging_client import LoggingClient
from src.core.utils.exceptions import ValidationException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session

logging_client = LoggingClient(service_name=settings.SERVICE_NAME)


class AuthManager:
    """
    Manages user authentication and authorization logic.
    """

    def __init__(
        self,
        user_repository: UserRepository = Depends(),
        session_repository: SessionRepository = Depends(),
        session: AsyncSession = Depends(get_session),
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.session = session

    @handle_exceptions
    async def register_user(self, email: str, password: str) -> None:
        """Registers a new user."""
        logging_client.info(f"Registering new user with email: {email}")

        if not email or not password:
            logging_client.warning("Email or password cannot be empty.")
            raise ValidationException("Email and password are required")

        hashed_password = self.pwd_context.hash(password)
        try:
            await self.user_repository.create(
                email=email, hashed_password=hashed_password
            )
            logging_client.info(f"User registered successfully with email: {email}")
        except Exception as e:
           logging_client.error(f"Error during user registration with email {email}: {e}")
           raise

    @handle_exceptions
    async def login_user(self, email: str, password: str) -> Dict[str, str]:
        """Authenticates a user and returns JWT tokens."""
        logging_client.info(f"Authenticating user with email: {email}")

        user = await self.user_repository.get_by_email(email=email)
        if not user:
            logging_client.warning(f"User with email {email} not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not self.pwd_context.verify(password, user.hashed_password):
            logging_client.warning(f"Invalid password for user with email {email}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        access_token = self._create_token(user_id=user.id, token_type="access")
        refresh_token = self._create_token(user_id=user.id, token_type="refresh")

        await self.session_repository.create(user_id=user.id, refresh_token=refresh_token, expires_at=datetime.utcnow() + timedelta(hours=24))
        logging_client.info(f"User with email {email} successfully authenticated.")

        return {"access_token": access_token, "refresh_token": refresh_token}

    @handle_exceptions
    async def logout_user(self, refresh_token: str) -> None:
        """Invalidates a refresh token and logs out user."""
        logging_client.info("Logging out user with refresh token")
        try:
            session = await self.session_repository.get_by_refresh_token(refresh_token=refresh_token)
            if not session:
                logging_client.warning("Invalid or expired refresh token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                 )
            await self.session_repository.delete_by_refresh_token(refresh_token=refresh_token)
            logging_client.info("User logged out successfully.")
        except Exception as e:
            logging_client.error(f"Error during logout, {e}")
            raise


    @handle_exceptions
    def _create_token(self, user_id: int, token_type: str) -> str:
        """Creates a JWT token."""
        logging_client.debug(f"Creating token of type: {token_type} for user_id: {user_id}")
        
        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=15)
            payload = {"user_id": user_id, "type": token_type, "exp": expire}
        elif token_type == "refresh":
            expire = datetime.utcnow() + timedelta(hours=24)
            payload = {"user_id": user_id, "type": token_type, "exp": expire}
        else:
            logging_client.warning(f"Invalid token type: {token_type}")
            raise ValueError("Invalid token type")
        
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")
        logging_client.debug(f"Token of type {token_type} created for user_id {user_id}.")
        return token

    @handle_exceptions
    async def get_user_by_token(self, access_token: str) -> Optional[dict]:
        """
        Retrieves user data based on a valid JWT access token.
        """
        logging_client.info("Getting user data by token")
        try:
            payload = jwt.decode(
                 access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            user = await self.user_repository.get(user_id=user_id)
            if user:
                logging_client.info(f"User data retrieved successfully for user_id {user_id}.")
                return {"id": user.id, "email": user.email, "roles": ["admin"] if user.email == "admin@admin.com" else ["user"]}
            else:
                 logging_client.warning("User not found for decoded token.")
                 return None
        except jwt.ExpiredSignatureError:
            logging_client.warning("Token has expired.")
            return None
        except jwt.InvalidTokenError:
            logging_client.warning("Invalid token.")
            return None
        except Exception as e:
            logging_client.error(f"Unexpected error during token decode or user retrieval: {e}")
            return None
    
    @handle_exceptions
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
            """
            Refreshes the access token using the refresh token.
            """
            logging_client.info("Refreshing token")
            try:
                session = await self.session_repository.get_by_refresh_token(refresh_token=refresh_token)
                if not session:
                    logging_client.warning("Invalid or expired refresh token")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired refresh token"
                    )
                user = await self.user_repository.get(user_id=session.user_id)
                if not user:
                    logging_client.warning(f"User for refresh token not found")
                    raise HTTPException(
                       status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                    )
                access_token = self._create_token(user_id=user.id, token_type="access")
                new_refresh_token = self._create_token(user_id=user.id, token_type="refresh")
                
                await self.session_repository.delete_by_refresh_token(refresh_token=refresh_token)
                await self.session_repository.create(user_id=user.id, refresh_token=new_refresh_token, expires_at=datetime.utcnow() + timedelta(hours=24))
                
                logging_client.info("Token refreshed successfully")
                return {"access_token": access_token, "refresh_token": new_refresh_token}
            except Exception as e:
                logging_client.error(f"Error refreshing token, {e}")
                raise