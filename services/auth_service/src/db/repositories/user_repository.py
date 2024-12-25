# services/auth_service/src/db/repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from src.db.models.user_model import User
from src.db.models.role_model import Role
from loguru import logger
from typing import Optional, List

from src.db.repositories.role_repository import RoleRepositoryError, RoleNotFoundError

class UserRepositoryError(Exception):
    pass

class UserNotFoundError(UserRepositoryError):
    pass

class UserCreationError(UserRepositoryError):
    pass 

class UserUpdateError(UserRepositoryError):
    pass

class UserDeletionError(UserRepositoryError):
    pass

class RoleAssignmentError(UserRepositoryError):
    pass

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            q = select(User).where(User.email == email).options(selectinload(User.roles))  
            result = await self.session.execute(q)
            user = result.unique().scalar_one_or_none()
            if user:
                logger.debug(f"Found user with email: {email}")
            else:
                logger.debug(f"No user found with email: {email}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting user by email {email}: {str(e)}")
            raise UserRepositoryError("Failed to retrieve user") from e
        except Exception as e:
            logger.error(f"Unexpected error while getting user by email {email}: {str(e)}")
            raise UserRepositoryError("An unexpected error occurred while retrieving user") from e

    async def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            q = select(User).where(User.id == user_id).options(selectinload(User.roles))
            result = await self.session.execute(q)
            user = result.unique().scalar_one_or_none()
            if user:
                logger.debug(f"Found user with ID: {user_id}")
            else:
                logger.debug(f"No user found with ID: {user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting user by ID {user_id}: {str(e)}")
            raise UserRepositoryError("Failed to retrieve user") from e
        except Exception as e:
            logger.error(f"Unexpected error while getting user by ID {user_id}: {str(e)}")
            raise UserRepositoryError("An unexpected error occurred while retrieving user") from e

    async def create_user(self, email: str, hashed_password: str) -> User:
        try:
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                is_active=True
            )
            self.session.add(new_user)
            await self.session.flush()
            logger.debug(f"User object created: {new_user.email}, hash: {new_user.hashed_password[:20]}...")
            
            await self.session.commit()
            await self.session.refresh(new_user)
            logger.info(f"User successfully created with email: {email}")
            return new_user
            
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while creating user {email}: {str(e)}")
            raise UserCreationError("Failed to create user") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while creating user {email}: {str(e)}")
            raise UserCreationError("An unexpected error occurred while creating user") from e

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        try:
            stmt = update(User).where(User.id == user_id)
            updates = {}
            if 'email' in kwargs:
                updates["email"] = kwargs['email']
            if 'hashed_password' in kwargs:
                updates["hashed_password"] = kwargs['hashed_password']
            if 'is_active' in kwargs:
                updates["is_active"] = kwargs['is_active']

            stmt = stmt.values(**updates).options(selectinload(User.roles)).returning(User)
            result = await self.session.execute(stmt)
            user = result.unique().scalar_one_or_none()
            if user:
                await self.session.commit()
                logger.info(f"User with ID {user_id} updated successfully")
                logger.debug(f"Updated fields: {updates}")
                return user
            else:
                logger.warning(f"No user found with ID {user_id} for update")
                return None
                
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while updating user {user_id}: {str(e)}")
            raise UserUpdateError("Failed to update user") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while updating user {user_id}: {str(e)}")
            raise UserUpdateError("An unexpected error occurred while updating user") from e

    async def delete_user(self, user_id: int) -> bool:
        try:
            stmt = delete(User).where(User.id == user_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while deleting user {user_id}: {str(e)}")
            raise UserDeletionError("Failed to delete user") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while deleting user {user_id}: {str(e)}")
            raise UserDeletionError("An unexpected error occurred while deleting user") from e

    async def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        try:
            user = await self.get_by_id(user_id)
            if not user:
                logger.error(f"User with ID {user_id} not found")
                raise UserNotFoundError(f"User with ID {user_id} not found")

            role = await self.session.get(Role, role_id)
            if not role:
                logger.error(f"Role with ID {role_id} not found")
                raise RoleNotFoundError(f"Role with ID {role_id} not found")

            if role in user.roles:
                logger.info(f"User (ID: {user_id}) already has role (ID: {role_id})")
                return

            user.roles.append(role)
            await self.session.commit()
            logger.info(f"Role (ID: {role_id}) successfully assigned to user (ID: {user_id})")
        except RoleNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while assigning role {role_id} to user {user_id}: {str(e)}")
            raise RoleAssignmentError("Failed to assign role to user") from e
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while assigning role {role_id} to user {user_id}: {str(e)}")
            raise RoleAssignmentError("An unexpected error occurred while assigning role to user") from e

    async def bulk_update_user_roles(self, user_ids: List[int], role_ids: List[int]) -> None:
        try:
            users = await self.session.execute(
                select(User).where(User.id.in_(user_ids)).options(selectinload(User.roles))
            )
            users = users.unique().scalars().all()

            roles = await self.session.execute(
                select(Role).where(Role.id.in_(role_ids))
            )
            roles = roles.unique().scalars().all()

            for user in users:
                user.roles = roles
            
            await self.session.commit()
            logger.info(f"Successfully updated roles for {len(users)} users")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Database error while bulk updating user roles: {str(e)}")
            raise UserUpdateError("Failed to bulk update user roles") from e  
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error while bulk updating user roles: {str(e)}")
            raise UserUpdateError("An unexpected error occurred while bulk updating user roles") from e