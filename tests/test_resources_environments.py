"""Tests for Energy Tracker API environment resources."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.models import (
    CreateEnvironmentEntryDto,
    CreateEnvironmentRecordDto,
)
from energy_tracker_api.resources.environments import EnvironmentResource


class TestEnvironmentResourceInitialization:
    """Tests for EnvironmentResource initialization."""

    def test_initialization(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)

        # Act
        resource = EnvironmentResource(client)

        # Assert
        assert resource._client == client


class TestEnvironmentResourceList:
    """Tests for EnvironmentResource.list method."""

    @pytest.mark.asyncio
    async def test_list_environments(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value=[
                {
                    "id": "env-1",
                    "title": "Temperature",
                    "unit": "°C",
                    "entries": [{"timestamp": "2024-01-15T10:00:00.000Z", "value": 22.0}],
                },
                {
                    "id": "env-2",
                    "title": "Humidity",
                    "unit": "%",
                    "entries": [],
                },
            ]
        )
        resource = EnvironmentResource(client)

        # Act
        result = await resource.list(device_id="device-123")

        # Assert
        assert len(result) == 2
        assert result[0].id == "env-1"
        assert result[0].title == "Temperature"
        assert result[0].unit == "°C"
        assert len(result[0].entries) == 1
        assert result[0].entries[0].value == 22.0
        assert result[1].entries == []
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/standard/device-123/environments",
        )


class TestEnvironmentResourceGet:
    """Tests for EnvironmentResource.get method."""

    @pytest.mark.asyncio
    async def test_get_environment(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value={
                "id": "env-1",
                "title": "Temperature",
                "unit": "°C",
                "entries": [
                    {"timestamp": "2024-01-15T10:00:00.000Z", "value": 22.0},
                    {"timestamp": "2024-01-15T11:00:00.000Z", "value": 23.5},
                ],
            }
        )
        resource = EnvironmentResource(client)

        # Act
        result = await resource.get(device_id="device-123", environment_id="env-1")

        # Assert
        assert result.id == "env-1"
        assert result.title == "Temperature"
        assert len(result.entries) == 2
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/standard/device-123/environments/env-1",
        )


class TestEnvironmentResourceCreate:
    """Tests for EnvironmentResource.create method."""

    @pytest.mark.asyncio
    async def test_create_with_unit(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value={
                "id": "env-new",
                "title": "Temperature",
                "unit": "°C",
                "entries": [],
            }
        )
        resource = EnvironmentResource(client)
        dto = CreateEnvironmentRecordDto(title="Temperature", unit="°C")

        # Act
        result = await resource.create(device_id="device-123", environment_record=dto)

        # Assert
        assert result.id == "env-new"
        assert result.title == "Temperature"
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/environments",
            json={"title": "Temperature", "unit": "°C"},
        )

    @pytest.mark.asyncio
    async def test_create_without_unit(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value={
                "id": "env-new",
                "title": "Humidity",
                "entries": [],
            }
        )
        resource = EnvironmentResource(client)
        dto = CreateEnvironmentRecordDto(title="Humidity")

        # Act
        result = await resource.create(device_id="device-123", environment_record=dto)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/environments",
            json={"title": "Humidity"},
        )


class TestEnvironmentResourceDelete:
    """Tests for EnvironmentResource.delete method."""

    @pytest.mark.asyncio
    async def test_delete_environment(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = EnvironmentResource(client)

        # Act
        await resource.delete(device_id="device-123", environment_id="env-1")

        # Assert
        client._make_request.assert_called_once_with(
            method="DELETE",
            endpoint="/v1/devices/standard/device-123/environments/env-1",
        )


class TestEnvironmentResourceCreateEntry:
    """Tests for EnvironmentResource.create_entry method."""

    @pytest.mark.asyncio
    async def test_create_entry_with_value_only(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = EnvironmentResource(client)
        entry = CreateEnvironmentEntryDto(value=23.5)

        # Act
        await resource.create_entry(device_id="device-123", environment_id="env-1", entry=entry)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/environments/env-1",
            json={"value": 23.5},
        )

    @pytest.mark.asyncio
    async def test_create_entry_with_timestamp(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = EnvironmentResource(client)
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        entry = CreateEnvironmentEntryDto(value=23.5, timestamp=timestamp)

        # Act
        await resource.create_entry(device_id="device-123", environment_id="env-1", entry=entry)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/environments/env-1",
            json={"value": 23.5, "timestamp": "2024-01-15T10:30:45.123"},
        )

    @pytest.mark.asyncio
    async def test_create_entry_returns_none(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = EnvironmentResource(client)
        entry = CreateEnvironmentEntryDto(value=23.5)

        # Act
        result = await resource.create_entry(
            device_id="device-123", environment_id="env-1", entry=entry
        )

        # Assert
        assert result is None


class TestEnvironmentResourceDeleteEntry:
    """Tests for EnvironmentResource.delete_entry method."""

    @pytest.mark.asyncio
    async def test_delete_entry(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = EnvironmentResource(client)
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)

        # Act
        await resource.delete_entry(
            device_id="device-123", environment_id="env-1", timestamp=timestamp
        )

        # Assert
        client._make_request.assert_called_once_with(
            method="DELETE",
            endpoint="/v1/devices/standard/device-123/environments/env-1/entries",
            json={"timestamp": "2024-01-15T10:30:45.123"},
        )
