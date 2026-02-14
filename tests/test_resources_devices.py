"""Tests for Energy Tracker API device resources."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.resources.devices import DeviceResource


class TestDeviceResourceInitialization:
    """Tests for DeviceResource initialization."""

    def test_initialization(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)

        # Act
        resource = DeviceResource(client)

        # Assert
        assert resource._client == client


class TestDeviceResourceListStandard:
    """Tests for DeviceResource.list_standard method."""

    @pytest.mark.asyncio
    async def test_list_standard_without_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value=[
                {
                    "id": "device-1",
                    "name": "Gas Meter",
                    "folderPath": "/basement",
                    "lastUpdatedAt": "2024-01-15T10:00:00.000Z",
                },
                {
                    "id": "device-2",
                    "name": "Electricity",
                    "folderPath": "/main",
                    "lastUpdatedAt": None,
                },
            ]
        )
        resource = DeviceResource(client)

        # Act
        result = await resource.list_standard()

        # Assert
        assert len(result) == 2
        assert result[0].id == "device-1"
        assert result[0].name == "Gas Meter"
        assert result[0].folder_path == "/basement"
        assert result[1].id == "device-2"
        assert result[1].last_updated_at is None
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/standard",
            params=None,
        )

    @pytest.mark.asyncio
    async def test_list_standard_with_name_filter(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = DeviceResource(client)

        # Act
        await resource.list_standard(name="gas")

        # Assert
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/standard",
            params={"name": "gas"},
        )

    @pytest.mark.asyncio
    async def test_list_standard_with_folder_path_filter(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = DeviceResource(client)

        # Act
        await resource.list_standard(folder_path="/basement")

        # Assert
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/standard",
            params={"folderPath": "/basement"},
        )

    @pytest.mark.asyncio
    async def test_list_standard_with_timestamp_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = DeviceResource(client)
        after = datetime(2024, 1, 1)
        before = datetime(2024, 12, 31)

        # Act
        await resource.list_standard(updated_after=after, updated_before=before)

        # Assert
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/standard",
            params={
                "updatedAfter": "2024-01-01T00:00:00.000",
                "updatedBefore": "2024-12-31T00:00:00.000",
            },
        )

    @pytest.mark.asyncio
    async def test_list_standard_returns_empty_list(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = DeviceResource(client)

        # Act
        result = await resource.list_standard()

        # Assert
        assert result == []


class TestDeviceResourceListVirtual:
    """Tests for DeviceResource.list_virtual method."""

    @pytest.mark.asyncio
    async def test_list_virtual_without_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value=[
                {
                    "id": "virtual-1",
                    "name": "Total Consumption",
                    "folderPath": "/",
                    "lastUpdatedAt": None,
                }
            ]
        )
        resource = DeviceResource(client)

        # Act
        result = await resource.list_virtual()

        # Assert
        assert len(result) == 1
        assert result[0].id == "virtual-1"
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/virtual",
            params=None,
        )

    @pytest.mark.asyncio
    async def test_list_virtual_with_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = DeviceResource(client)

        # Act
        await resource.list_virtual(name="total", folder_path="/")

        # Assert
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/devices/virtual",
            params={"name": "total", "folderPath": "/"},
        )
