from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from sqlalchemy.orm import relationship
from .base import Base


class Log(Base):
    """
    SQLAlchemy model for storing log entries in the database.
    """

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(255), nullable=False, index=True)
    service = Column(String(255), nullable=False, index=True)
    message = Column(String(1000), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', service='{self.service}')>"