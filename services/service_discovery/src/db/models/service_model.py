from sqlalchemy import Column, Integer, String, DateTime, func, JSON, Boolean
from .base import Base


class Service(Base):
    """
    SQLAlchemy model for storing service information in the database.
    """

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="healthy")

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}')>"