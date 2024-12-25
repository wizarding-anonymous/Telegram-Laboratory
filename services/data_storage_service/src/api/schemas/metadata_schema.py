# services\data_storage_service\src\api\schemas\metadata_schema.py
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class MetadataCreate(BaseModel):
    """
    Схема для создания новых метаданных для бота.
    """

    bot_id: int = Field(..., description="ID бота, для которого создаются метаданные")
    metadata_key: str = Field(..., max_length=255, description="Ключ метаданных")
    metadata_value: Any = Field(..., description="Значение метаданных")

    @validator("metadata_key")
    def validate_metadata_key(cls, value):
        """
        Валидация ключа метаданных: должно быть строкой, не пустым и без специальных символов.
        """
        if not value.strip():
            raise ValueError("Metadata key cannot be empty.")
        if len(value) > 255:
            raise ValueError("Metadata key cannot exceed 255 characters.")
        return value.strip()


class MetadataUpdate(BaseModel):
    """
    Схема для обновления существующих метаданных для бота.
    """

    metadata_key: Optional[str] = Field(
        None, max_length=255, description="Обновленный ключ метаданных"
    )
    metadata_value: Optional[Any] = Field(
        None, description="Обновленное значение метаданных"
    )

    @validator("metadata_key")
    def validate_metadata_key(cls, value):
        """
        Валидация ключа метаданных при обновлении (если оно передано).
        """
        if value and not value.strip():
            raise ValueError("Metadata key cannot be empty.")
        if value and len(value) > 255:
            raise ValueError("Metadata key cannot exceed 255 characters.")
        return value


class MetadataResponse(BaseModel):
    """
    Схема для возвращаемых данных о метаданных.
    """

    id: int = Field(..., description="ID метаданных")
    bot_id: int = Field(..., description="ID бота, к которому относятся метаданные")
    metadata_key: str = Field(..., description="Ключ метаданных")
    metadata_value: Any = Field(..., description="Значение метаданных")
    created_at: str = Field(..., description="Дата и время создания метаданных")
    updated_at: Optional[str] = Field(
        None, description="Дата и время последнего обновления метаданных"
    )

    class Config:
        from_attributes = True  # Для преобразования ORM объектов в Pydantic модели


class MetadataListResponse(BaseModel):
    """
    Схема для возвращаемого списка метаданных.
    """

    metadata: list[MetadataResponse] = Field(..., description="Список метаданных")
    total: int = Field(..., description="Общее количество метаданных")
