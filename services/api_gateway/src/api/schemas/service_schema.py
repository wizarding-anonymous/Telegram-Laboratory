# services/api_gateway/src/api/schemas/service_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ServiceBase(BaseModel):
    # Базовая модель для всех сервисов
    name: str  # Название сервиса
    status: str  # Статус сервиса (например, "running", "stopped")
    last_checked: datetime  # Время последней проверки статуса
    description: Optional[str] = None  # Описание сервиса (по желанию)
    
    class Config:
        orm_mode = True

class ServiceCreate(ServiceBase):
    # Модель для создания сервиса
    pass

class ServiceUpdate(ServiceBase):
    # Модель для обновления информации о сервисе
    pass

class Service(ServiceBase):
    # Модель для представления сервиса в ответах
    id: int  # ID сервиса в базе данных
    created_at: datetime  # Время создания записи о сервисе
    updated_at: datetime  # Время последнего обновления
    
    class Config:
        orm_mode = True

class ServiceListResponse(BaseModel):
    # Ответ для получения списка всех сервисов
    services: List[Service]  # Список сервисов
    
    class Config:
        orm_mode = True

class ServiceDetailResponse(BaseModel):
    # Ответ для получения детализированной информации о сервисе
    service: Service  # Детальная информация о сервисе
    
    class Config:
        orm_mode = True

class ServiceHealthCheckResponse(BaseModel):
    # Ответ для проверки состояния сервиса
    service_name: str  # Название сервиса
    is_healthy: bool  # Состояние сервиса (здоров или нет)
    last_checked: datetime  # Время последней проверки
    status_message: Optional[str] = None  # Сообщение о состоянии (например, "Service is running")
    
    class Config:
        orm_mode = True

class ServiceHealthCheckRequest(BaseModel):
    # Запрос для выполнения проверки состояния сервиса
    service_name: str  # Название сервиса для проверки состояния
    
    class Config:
        orm_mode = True
