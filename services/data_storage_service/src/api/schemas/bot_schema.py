# services\data_storage_service\src\api\schemas\bot_schema.py
import string
from typing import Optional

from pydantic import BaseModel, Field, validator


class BotCreate(BaseModel):
    """
    Схема для создания нового бота.
    """

    user_id: int = Field(..., description="ID пользователя, который создает бота")
    name: str = Field(..., max_length=255, description="Имя бота")
    description: Optional[str] = Field(
        None, max_length=1000, description="Описание бота"
    )

    @validator("name")
    def validate_name(cls, value):
        """
        Валидация имени бота: должно быть строкой, не пустым, не содержать спецсимволов.
        """
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        if any(char in string.punctuation for char in value):
            raise ValueError("Name cannot contain special characters.")
        return value.strip()


class BotUpdate(BaseModel):
    """
    Схема для обновления существующего бота.
    """

    name: Optional[str] = Field(None, max_length=255, description="Новое имя бота")
    description: Optional[str] = Field(
        None, max_length=1000, description="Обновленное описание бота"
    )

    @validator("name", always=True)
    def validate_name(cls, value):
        """
        Валидация имени бота при обновлении (если оно передано).
        """
        if value and not value.strip():
            raise ValueError("Name cannot be empty.")
        if value and any(char in string.punctuation for char in value):
            raise ValueError("Name cannot contain special characters.")
        return value


class BotResponse(BaseModel):
    """
    Схема для ответа API, содержащая данные о боте.
    """

    id: int = Field(..., description="ID бота")
    user_id: int = Field(..., description="ID пользователя, который владеет ботом")
    name: str = Field(..., description="Имя бота")
    description: Optional[str] = Field(None, description="Описание бота")
    created_at: str = Field(..., description="Дата и время создания бота")
    updated_at: Optional[str] = Field(
        None, description="Дата и время последнего обновления бота"
    )

    class Config:
        from_attributes = True  # Для преобразования ORM объектов в Pydantic модели

    @property
    def user(self):
        """
        Геттер для пользователя, который создал бота.
        """
        return {"user_id": self.user_id}


class BotListResponse(BaseModel):
    """
    Схема для возвращаемого списка ботов.
    """

    bots: list[BotResponse] = Field(..., description="Список ботов")
    total: int = Field(..., description="Общее количество ботов")
