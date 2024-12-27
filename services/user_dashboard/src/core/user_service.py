# user_dashboard/src/core/user_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from user_dashboard.src.models.user_model import User
from user_dashboard.src.schemas.user_schema import UserProfileUpdate

async def get_user_profile(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise ValueError("User not found")
    return user

async def update_user_profile(db: AsyncSession, user_id: int, profile_update: UserProfileUpdate) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise ValueError("User not found")
    
    if profile_update.name:
        user.name = profile_update.name
    if profile_update.email:
        user.email = profile_update.email
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def initiate_password_reset(db: AsyncSession, email: str) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise ValueError("Email not found")
    
    # Здесь реализуйте логику отправки email для сброса пароля
    # Например, генерирование токена сброса и отправка его на email пользователя

async def change_user_password(db: AsyncSession, user_id: int, new_hashed_password: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise ValueError("User not found")
    
    user.hashed_password = new_hashed_password
    db.add(user)
    await db.commit()
