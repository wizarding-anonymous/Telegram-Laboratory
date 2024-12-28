from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base
from sqlalchemy.orm import relationship


class Variable(Base):
    """
    Model for storing variable block information.
    """

    __tablename__ = "variables"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False, default="variable")
    name = Column(String(255), nullable=False)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connections = relationship("Connection",
                                 primaryjoin="Variable.id==Connection.source_block_id",
                                 cascade="all, delete-orphan",
                                 lazy="selectin",
                                 )


    def __repr__(self):
        return f"<Variable(id={self.id}, type='{self.type}', name='{self.name}', value='{self.value}')>"