from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from .base import Base


class Bot(Base):
    """
    SQLAlchemy model for storing bot information in meta-database.
    """

    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Bot(id={self.id}, name='{self.name}')>"