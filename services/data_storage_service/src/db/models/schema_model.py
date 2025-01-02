from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from .base import Base


class Schema(Base):
    """
    SQLAlchemy model for storing database connection strings (DSNs)
    for individual bot databases.
    """

    __tablename__ = "schemas"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    dsn = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    def __repr__(self):
        return f"<Schema(id={self.id}, bot_id={self.bot_id}, dsn='{self.dsn}')>"