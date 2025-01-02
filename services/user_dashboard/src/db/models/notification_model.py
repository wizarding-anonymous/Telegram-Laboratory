from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from .base import Base


class Notification(Base):
    """
    SQLAlchemy model for storing user notification information in the database.
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(255), nullable=False, default="unread")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}')>"