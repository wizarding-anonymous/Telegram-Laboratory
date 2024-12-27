# user_dashboard/src/core/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from app.models.user_model import User
from app.schemas.user_schema import UserCreateRequest, UserUpdateRequest, UserResponse
from datetime import datetime
import logging

logger = logging.getLogger("user_service")


class UserService:
    """
    Сервис для управления данными пользователей.
    """

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreateRequest) -> UserResponse:
        """
        Создает нового пользователя.
        """
        try:
            new_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=user_data.password,  # Предполагается хэширование
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info(f"User created: {new_user.email} (ID: {new_user.id})")
            return UserResponse.from_orm(new_user)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserResponse:
        """
        Возвращает данные пользователя по ID.
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"User not found: ID {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return UserResponse.from_orm(user)
        except Exception as e:
            logger.error(f"Error fetching user ID {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user")

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdateRequest) -> UserResponse:
        """
        Обновляет данные существующего пользователя.
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"User not found: ID {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            if user_data.full_name:
                user.full_name = user_data.full_name
            if user_data.password:
                user.hashed_password = user_data.password  # Предполагается хэширование
            user.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(user)

            logger.info(f"User updated: ID {user_id}")
            return UserResponse.from_orm(user)
        except Exception as e:
            logger.error(f"Error updating user ID {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        """
        Удаляет пользователя по ID.
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.warning(f"User not found: ID {user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            await db.delete(user)
            await db.commit()

            logger.info(f"User deleted: ID {user_id}")
        except Exception as e:
            logger.error(f"Error deleting user ID {user_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")

    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[UserResponse]:
        """
        Возвращает список всех пользователей.
        """
        try:
            result = await db.execute(select(User).options(joinedload(User.roles)))
            users = result.scalars().all()
            return [UserResponse.from_orm(user) for user in users]
        except Exception as e:
            logger.error(f"Error fetching all users: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch users")
