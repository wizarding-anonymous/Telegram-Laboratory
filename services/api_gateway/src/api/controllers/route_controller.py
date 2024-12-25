# services\api_gateway\src\api\controllers\route_controller.py
from typing import Dict, List, Optional
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.utils.route_validator import validate_route_data
from src.db.repositories.route_repository import RouteRepository
from src.api.schemas.route_schema import RouteCreate, RouteUpdate, RouteResponse
from src.api.schemas.response_schema import SuccessResponse
from src.integrations.auth_service import AuthService
from src.integrations.service_discovery import ServiceDiscovery
from src.core.utils.helpers import handle_exceptions


class RouteController:
    """
    Контроллер для управления маршрутами API Gateway.
    Обеспечивает CRUD операции для маршрутов и их взаимодействие с Service Discovery.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация контроллера с необходимыми зависимостями.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
        """
        self.session = session
        self.repository = RouteRepository(session)
        self.auth_service = AuthService()
        self.service_discovery = ServiceDiscovery()

    @handle_exceptions
    async def create_route(self, route_data: RouteCreate, user_id: int) -> RouteResponse:
        """
        Создает новый маршрут в API Gateway.

        Args:
            route_data (RouteCreate): Данные для создания маршрута.
            user_id (int): ID пользователя, создающего маршрут.

        Returns:
            RouteResponse: Информация о созданном маршруте.

        Raises:
            HTTPException: При ошибке создания маршрута или отсутствии прав.
        """
        # Проверяем права пользователя
        await self.auth_service.validate_user_permissions(user_id, "create_route")

        # Валидируем данные маршрута
        validate_route_data(route_data.dict())

        # Проверяем доступность целевого сервиса
        service_available = await self.service_discovery.check_service_availability(
            route_data.destination_url
        )
        if not service_available:
            raise HTTPException(
                status_code=404,
                detail=f"Service at {route_data.destination_url} is not available"
            )

        # Создаем маршрут
        route = await self.repository.create(route_data.dict())
        
        # Регистрируем маршрут в Service Discovery
        await self.service_discovery.register_route(route_data.dict())

        logger.info(f"Created route: {route.path} -> {route.destination_url}")
        return RouteResponse.from_orm(route)

    @handle_exceptions
    async def get_routes(self, skip: int = 0, limit: int = 100) -> List[RouteResponse]:
        """
        Получает список маршрутов с пагинацией.

        Args:
            skip (int): Количество пропускаемых записей.
            limit (int): Максимальное количество возвращаемых записей.

        Returns:
            List[RouteResponse]: Список маршрутов.
        """
        routes = await self.repository.get_all(skip=skip, limit=limit)
        return [RouteResponse.from_orm(route) for route in routes]

    @handle_exceptions
    async def get_route(self, route_id: int) -> Optional[RouteResponse]:
        """
        Получает информацию о конкретном маршруте.

        Args:
            route_id (int): ID маршрута.

        Returns:
            Optional[RouteResponse]: Информация о маршруте, если найден.

        Raises:
            HTTPException: Если маршрут не найден.
        """
        route = await self.repository.get_by_id(route_id)
        if not route:
            raise HTTPException(
                status_code=404,
                detail=f"Route with id {route_id} not found"
            )
        return RouteResponse.from_orm(route)

    @handle_exceptions
    async def update_route(
        self, 
        route_id: int, 
        route_data: RouteUpdate, 
        user_id: int
    ) -> RouteResponse:
        """
        Обновляет существующий маршрут.

        Args:
            route_id (int): ID маршрута для обновления.
            route_data (RouteUpdate): Новые данные маршрута.
            user_id (int): ID пользователя, выполняющего обновление.

        Returns:
            RouteResponse: Обновленная информация о маршруте.

        Raises:
            HTTPException: При ошибке обновления или отсутствии прав.
        """
        # Проверяем права пользователя
        await self.auth_service.validate_user_permissions(user_id, "update_route")

        # Проверяем существование маршрута
        existing_route = await self.repository.get_by_id(route_id)
        if not existing_route:
            raise HTTPException(
                status_code=404,
                detail=f"Route with id {route_id} not found"
            )

        # Валидируем новые данные
        validate_route_data(route_data.dict(exclude_unset=True))

        # Если меняется destination_url, проверяем доступность нового сервиса
        if route_data.destination_url:
            service_available = await self.service_discovery.check_service_availability(
                route_data.destination_url
            )
            if not service_available:
                raise HTTPException(
                    status_code=404,
                    detail=f"Service at {route_data.destination_url} is not available"
                )

        # Обновляем маршрут
        updated_route = await self.repository.update(
            route_id, 
            route_data.dict(exclude_unset=True)
        )

        # Обновляем информацию в Service Discovery
        await self.service_discovery.update_route(route_id, route_data.dict(exclude_unset=True))

        logger.info(f"Updated route {route_id}: {updated_route.path} -> {updated_route.destination_url}")
        return RouteResponse.from_orm(updated_route)

    @handle_exceptions
    async def delete_route(self, route_id: int, user_id: int) -> SuccessResponse:
        """
        Удаляет маршрут.

        Args:
            route_id (int): ID маршрута для удаления.
            user_id (int): ID пользователя, выполняющего удаление.

        Returns:
            SuccessResponse: Сообщение об успешном удалении.

        Raises:
            HTTPException: При ошибке удаления или отсутствии прав.
        """
        # Проверяем права пользователя
        await self.auth_service.validate_user_permissions(user_id, "delete_route")

        # Проверяем существование маршрута
        existing_route = await self.repository.get_by_id(route_id)
        if not existing_route:
            raise HTTPException(
                status_code=404,
                detail=f"Route with id {route_id} not found"
            )

        # Удаляем маршрут
        deleted = await self.repository.delete(route_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Route with id {route_id} not found or already deleted"
            )

        # Удаляем маршрут из Service Discovery
        await self.service_discovery.deregister_route(route_id)

        logger.info(f"Deleted route {route_id}")
        return SuccessResponse(message="Route deleted successfully")

    @handle_exceptions
    async def get_route_by_path(self, path: str) -> Optional[RouteResponse]:
        """
        Получает информацию о маршруте по его пути.

        Args:
            path (str): Путь маршрута.

        Returns:
            Optional[RouteResponse]: Информация о маршруте, если найден.

        Raises:
            HTTPException: Если маршрут не найден.
        """
        route = await self.repository.get_by_path(path)
        if not route:
            raise HTTPException(
                status_code=404,
                detail=f"Route with path {path} not found"
            )
        return RouteResponse.from_orm(route)

    @handle_exceptions
    async def cache_route(self, route_id: int) -> Dict[str, str]:
        """
        Кеширует маршрут для быстрого доступа.

        Args:
            route_id (int): ID маршрута для кеширования.

        Returns:
            Dict[str, str]: Статус операции кеширования.

        Raises:
            HTTPException: При ошибке кеширования.
        """
        try:
            route = await self.repository.get_by_id(route_id)
            if not route:
                raise HTTPException(
                    status_code=404,
                    detail=f"Route with id {route_id} not found"
                )

            # Здесь может быть логика кеширования маршрута
            return {"status": "Route cached successfully"}

        except Exception as e:
            logger.error(f"Error caching route {route_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error caching route: {str(e)}"
            )