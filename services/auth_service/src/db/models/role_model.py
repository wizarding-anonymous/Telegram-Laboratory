from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from sqlalchemy.orm import relationship
from .base import Base


class Role(Base):
    """
    SQLAlchemy model for storing user role information in the database.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    permissions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"