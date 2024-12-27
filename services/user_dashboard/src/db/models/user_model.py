# user_dashboard/src/models/user_model.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from user_dashboard.src.db.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bots = relationship("Bot", back_populates="owner")
