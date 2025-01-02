from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from .base import Base


class Metadata(Base):
    """
    SQLAlchemy model for storing metadata for a bot in meta-database.
    """

    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    value = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Metadata(id={self.id}, key='{self.key}', bot_id='{self.bot_id}')>"