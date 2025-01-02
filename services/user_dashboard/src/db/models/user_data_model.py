from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship

from .base import Base


class UserData(Base):
    """
    SQLAlchemy model for storing user-specific data and analytics for each bot in the database.
    """

    __tablename__ = "user_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bot_id = Column(Integer, nullable=False, index=True)
    analytics = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserData(id={self.id}, user_id={self.user_id}, bot_id={self.bot_id})>"