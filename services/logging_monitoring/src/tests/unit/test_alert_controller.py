import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException, status

from src.api.controllers import AlertController
from src.api.schemas import AlertCreate, AlertUpdate
from src.core.alert_manager import AlertManager


@pytest.fixture
def mock_alert_manager() -> AsyncMock:
    """
    Fixture to create a mock AlertManager.
    """
    return AsyncMock(spec=AlertManager)


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """
    Fixture to create a mock AuthService.
    """
    mock = AsyncMock()
    mock.get_user_by_token.return_value = {"id": 1, "roles": ["admin"]}
    return mock

@pytest.mark.asyncio
async def test_create_alert_success(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the create_alert method successfully creates an alert rule.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    alert_data = AlertCreate(
        metric="cpu_usage", threshold=80, operator=">", notification_channel="email"
    )
    mock_alert_manager.create_alert.return_value = AsyncMock(
        id=1, metric="cpu_usage", threshold=80, operator=">", notification_channel="email", created_at="test_time"
    )
    result = await controller.create_alert(alert_data=alert_data, user={"id": 1})
    assert result.id == 1
    assert result.metric == "cpu_usage"
    assert result.threshold == 80
    assert result.operator == ">"
    mock_alert_manager.create_alert.assert_called_once()


@pytest.mark.asyncio
async def test_get_alert_success(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_alert method successfully retrieves an alert rule.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    mock_alert_manager.get_alert.return_value = AsyncMock(
       id=1, metric="cpu_usage", threshold=80, operator=">", notification_channel="email", created_at="test_time"
    )

    result = await controller.get_alert(alert_id=1, user={"id": 1})

    assert result.id == 1
    assert result.metric == "cpu_usage"
    assert result.threshold == 80
    assert result.operator == ">"
    mock_alert_manager.get_alert.assert_called_once()


@pytest.mark.asyncio
async def test_get_alert_not_found(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_alert method raises an HTTPException if alert rule is not found.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    mock_alert_manager.get_alert.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.get_alert(alert_id=1, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_alerts_success(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the get_all_alerts method successfully retrieves all alert rules.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    mock_alert_manager.get_all_alerts.return_value = [
        AsyncMock(id=1, metric="cpu_usage", threshold=80, operator=">", notification_channel="email", created_at="test_time"),
        AsyncMock(id=2, metric="memory_usage", threshold=90, operator="<", notification_channel="slack", created_at="test_time"),
    ]

    result = await controller.get_all_alerts(user={"id": 1})

    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[1].id == 2
    mock_alert_manager.get_all_alerts.assert_called_once()


@pytest.mark.asyncio
async def test_update_alert_success(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the update_alert method successfully updates an alert rule.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    alert_data = AlertUpdate(metric="memory_usage", threshold=90, operator="<", notification_channel="slack")
    mock_alert_manager.get_alert.return_value = AsyncMock(
        id=1, metric="cpu_usage", threshold=80, operator=">", notification_channel="email", created_at="test_time"
    )
    mock_alert_manager.update_alert.return_value = AsyncMock(
       id=1, metric="memory_usage", threshold=90, operator="<", notification_channel="slack", created_at="test_time"
    )

    result = await controller.update_alert(alert_id=1, alert_data=alert_data, user={"id": 1})

    assert result.id == 1
    assert result.metric == "memory_usage"
    assert result.threshold == 90
    assert result.operator == "<"
    mock_alert_manager.update_alert.assert_called_once()
    mock_alert_manager.get_alert.assert_called_once()


@pytest.mark.asyncio
async def test_update_alert_not_found(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the update_alert method raises an HTTPException if alert rule is not found.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    alert_data = AlertUpdate(metric="memory_usage", threshold=90, operator="<", notification_channel="slack")
    mock_alert_manager.get_alert.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        await controller.update_alert(alert_id=1, alert_data=alert_data, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_alert_success(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the delete_alert method successfully deletes an alert rule.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    mock_alert_manager.get_alert.return_value = AsyncMock(
        id=1, metric="cpu_usage", threshold=80, operator=">", notification_channel="email", created_at="test_time"
    )

    result = await controller.delete_alert(alert_id=1, user={"id": 1})

    assert result.message == "Alert rule deleted successfully"
    mock_alert_manager.delete_alert.assert_called_once()
    mock_alert_manager.get_alert.assert_called_once()


@pytest.mark.asyncio
async def test_delete_alert_not_found(mock_alert_manager: AsyncMock, mock_auth_service: AsyncMock):
    """
    Test that the delete_alert method raises an HTTPException if alert rule is not found.
    """
    controller = AlertController(alert_manager=mock_alert_manager)
    mock_alert_manager.get_alert.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await controller.delete_alert(alert_id=1, user={"id": 1})
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND