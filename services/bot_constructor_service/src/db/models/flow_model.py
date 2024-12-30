from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base
from sqlalchemy.orm import relationship


class Flow(Base):
    """
    Model for storing flow chart block information.
    """

    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, default="flow_chart")
    logic = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connections = relationship("Connection",
                                 primaryjoin="Flow.id==Connection.source_block_id",
                                 cascade="all, delete-orphan",
                                 lazy="selectin",
                                 )

    def __repr__(self):
        return f"<Flow(id={self.id}, type='{self.type}', logic='{self.logic}')>"