# services/api_gateway/src/api/schemas/metric_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MetricBase(BaseModel):
    # Базовая модель для всех метрик
    service_name: str  # Название сервиса, который предоставляет метрики
    metric_name: str  # Название метрики (например, "cpu_usage", "memory_usage")
    timestamp: datetime  # Время, когда метрика была собрана
    value: float  # Значение метрики (например, процент использования процессора)
    
    class Config:
        orm_mode = True

class MetricCreate(MetricBase):
    # Модель для создания метрики
    pass

class MetricUpdate(MetricBase):
    # Модель для обновления метрики
    pass

class Metric(MetricBase):
    # Модель для представления метрики в ответах
    id: int  # ID метрики в базе данных
    
    class Config:
        orm_mode = True

class MetricsResponse(BaseModel):
    # Ответ на запрос метрик
    metrics: List[Metric]  # Список метрик
    
    class Config:
        orm_mode = True

class MetricAggregation(BaseModel):
    # Модель для агрегированных метрик
    metric_name: str  # Название метрики
    average_value: float  # Среднее значение метрики
    max_value: float  # Максимальное значение метрики
    min_value: float  # Минимальное значение метрики
    total_count: int  # Общее количество измерений
    
    class Config:
        orm_mode = True

class MetricAggregationResponse(BaseModel):
    # Ответ на запрос агрегированных метрик
    aggregated_metrics: List[MetricAggregation]  # Список агрегированных метрик
    
    class Config:
        orm_mode = True

