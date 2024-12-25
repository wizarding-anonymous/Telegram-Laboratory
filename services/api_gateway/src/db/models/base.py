# services\api_gateway\src\db\models\base.py
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class for all database models in the API Gateway service.
    Provides common functionality and fields for all models.
    """
    
    # Auto-incrementing primary key for all tables
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # SQLAlchemy requires these
    __name__: str
    __table__: Any
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generates table name from class name.
        Converts CamelCase to snake_case.
        Example: UserProfile -> user_profile
        """
        name = cls.__name__
        # Convert camel case to snake case
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        Excludes SQLAlchemy internal attributes.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        
    def update(self, **kwargs: Any) -> None:
        """
        Update model instance with provided keyword arguments.
        Only updates existing attributes.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base":
        """
        Create new model instance from dictionary data.
        Only sets attributes that exist in the model.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            New model instance
        """
        return cls(**{
            key: value 
            for key, value in data.items() 
            if hasattr(cls, key)
        })
        
    def merge(self, other: "Base") -> None:
        """
        Merge attributes from another model instance.
        Only updates existing attributes.
        
        Args:
            other: Another model instance to merge from
        """
        for column in self.__table__.columns:
            if hasattr(other, column.name):
                setattr(self, column.name, getattr(other, column.name))
                
    @classmethod
    def get_columns(cls) -> Dict[str, Any]:
        """
        Get dictionary of model columns and their types.
        
        Returns:
            Dictionary mapping column names to their SQLAlchemy types
        """
        return {
            column.name: column.type
            for column in cls.__table__.columns
        }
        
    def validate(self) -> Optional[Dict[str, str]]:
        """
        Validate model instance.
        Override in subclasses to add custom validation.
        
        Returns:
            Dictionary of validation errors or None if valid
        """
        return None
        
    def __repr__(self) -> str:
        """String representation of model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"