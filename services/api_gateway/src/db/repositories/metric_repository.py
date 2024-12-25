# services\api_gateway\src\db\repositories\metric_repository.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_

from src.db.models.metric_model import Metric
from src.core.exceptions import NotFoundException

class MetricRepository:
   """Repository for managing metrics data."""

   def __init__(self, session: AsyncSession):
       self._session = session

   async def create(self, metric_data: Dict[str, Any]) -> Metric:
       """Create new metric entry."""
       metric = Metric(**metric_data)
       self._session.add(metric)
       await self._session.flush()
       return metric

   async def get_by_id(self, metric_id: str) -> Optional[Metric]:
       """Get metric by ID."""
       query = select(Metric).where(Metric.id == metric_id)
       result = await self._session.execute(query)
       return result.scalar_one_or_none()

   async def get_service_metrics(
       self,
       service_name: str,
       start_time: Optional[datetime] = None,
       end_time: Optional[datetime] = None,
       metric_names: Optional[List[str]] = None
   ) -> List[Metric]:
       """Get metrics for specific service with filters."""
       query = select(Metric).where(Metric.service_name == service_name)

       if start_time:
           query = query.where(Metric.timestamp >= start_time)
       if end_time:
           query = query.where(Metric.timestamp <= end_time) 
       if metric_names:
           query = query.where(Metric.metric_name.in_(metric_names))

       result = await self._session.execute(query)
       return list(result.scalars().all())

   async def get_latest_metrics(
       self,
       service_name: str,
       metric_names: List[str]
   ) -> Dict[str, Metric]:
       """Get latest metrics for given metric names."""
       subquery = (
           select(
               Metric.metric_name,
               func.max(Metric.timestamp).label('max_timestamp')
           )
           .where(
               and_(
                   Metric.service_name == service_name,
                   Metric.metric_name.in_(metric_names)
               )
           )
           .group_by(Metric.metric_name)
           .subquery()
       )

       query = select(Metric).join(
           subquery,
           and_(
               Metric.metric_name == subquery.c.metric_name,
               Metric.timestamp == subquery.c.max_timestamp
           )
       )

       result = await self._session.execute(query)
       metrics = result.scalars().all()
       return {metric.metric_name: metric for metric in metrics}

   async def get_aggregated_metrics(
       self,
       service_name: str,
       metric_name: str,
       start_time: datetime,
       end_time: datetime,
       interval_minutes: int = 5
   ) -> List[Dict[str, Any]]:
       """Get aggregated metrics over time intervals."""
       interval = f'{interval_minutes} minutes'
       
       query = (
           select(
               func.time_bucket(interval, Metric.timestamp).label('bucket'),
               func.avg(Metric.metric_value).label('avg_value'),
               func.min(Metric.metric_value).label('min_value'),
               func.max(Metric.metric_value).label('max_value'),
               func.count(Metric.id).label('count')
           )
           .where(
               and_(
                   Metric.service_name == service_name,
                   Metric.metric_name == metric_name,
                   Metric.timestamp.between(start_time, end_time)
               )
           )
           .group_by('bucket')
           .order_by('bucket')
       )

       result = await self._session.execute(query)
       return [dict(row) for row in result]

   async def delete_old_metrics(
       self,
       service_name: str,
       older_than: datetime
   ) -> int:
       """Delete metrics older than specified time."""
       query = (
           Metric.__table__.delete()
           .where(
               and_(
                   Metric.service_name == service_name,
                   Metric.timestamp < older_than
               )
           )
       )
       result = await self._session.execute(query)
       return result.rowcount

   async def update_tags(
       self,
       metric_id: str,
       tags: Dict[str, Any]
   ) -> Metric:
       """Update metric tags."""
       metric = await self.get_by_id(metric_id)
       if not metric:
           raise NotFoundException(f"Metric {metric_id} not found")

       metric.tags = tags
       await self._session.flush()
       return metric

   async def count_by_service(
       self,
       service_name: str,
       start_time: Optional[datetime] = None,
       end_time: Optional[datetime] = None
   ) -> int:
       """Count metrics for service in time range."""
       query = select(func.count(Metric.id)).where(Metric.service_name == service_name)

       if start_time:
           query = query.where(Metric.timestamp >= start_time)
       if end_time:
           query = query.where(Metric.timestamp <= end_time)

       result = await self._session.execute(query)
       return result.scalar_one()