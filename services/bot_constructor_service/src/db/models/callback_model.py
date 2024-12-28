from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base
from sqlalchemy.orm import relationship


class Callback(Base):
    """
    Model for storing callback block information.
    """

    __tablename__ = "callbacks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, default="handle_callback_query")
    content = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connections = relationship("Connection",
                                 primaryjoin="Callback.id==Connection.source_block_id",
                                 cascade="all, delete-orphan",
                                 lazy="selectin",
                                 )


    def __repr__(self):
        return f"<Callback(id={self.id}, type='{self.type}', content='{self.content}')>"