"""Tests for Energy Tracker API resources."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.models import (
    CreateMeterReadingDto,
    ExportColumn,
    ExportMeterReadingsDto,
    SortDirection,
)
from energy_tracker_api.resources import MeterReadingResource


class TestMeterReadingResourceInitialization:
    """Tests for MeterReadingResource initialization."""

    def test_initialization(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)

        # Act
        resource = MeterReadingResource(client)

        # Assert
        assert resource._client == client


class TestMeterReadingResourceCreate:
    """Tests for MeterReadingResource.create method."""

    @pytest.mark.asyncio
    async def test_create_with_minimal_data(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"))

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"value": "123.45"},
            params=None,
        )

    @pytest.mark.asyncio
    async def test_create_with_timestamp(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"), timestamp=timestamp)

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"value": "123.45", "timestamp": "2024-01-15T10:30:45.123"},
            params=None,
        )

    @pytest.mark.asyncio
    async def test_create_with_note(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"), note="Manual reading")

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"value": "123.45", "note": "Manual reading"},
            params=None,
        )

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        meter_reading = CreateMeterReadingDto(
            value=Decimal("123.45"), timestamp=timestamp, note="Manual reading"
        )

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={
                "value": "123.45",
                "timestamp": "2024-01-15T10:30:45.123",
                "note": "Manual reading",
            },
            params=None,
        )

    @pytest.mark.asyncio
    async def test_create_with_allow_rounding_true(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"))

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading, allow_rounding=True)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"value": "123.45"},
            params={"allowRounding": "true"},
        )

    @pytest.mark.asyncio
    async def test_create_with_allow_rounding_false(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"))

        # Act
        await resource.create(
            device_id=device_id, meter_reading=meter_reading, allow_rounding=False
        )

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"value": "123.45"},
            params={"allowRounding": "false"},
        )

    @pytest.mark.asyncio
    async def test_create_with_allow_rounding_none(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"))

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading, allow_rounding=None)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"value": "123.45"},
            params=None,
        )

    @pytest.mark.asyncio
    async def test_create_with_different_device_id(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "another-device-456"
        meter_reading = CreateMeterReadingDto(value=Decimal("999.99"))

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/another-device-456/meter-readings",
            json={"value": "999.99"},
            params=None,
        )

    @pytest.mark.asyncio
    async def test_create_calls_to_dict_on_meter_reading(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = Mock(spec=CreateMeterReadingDto)
        meter_reading._to_dict.return_value = {"value": 100.0}

        # Act
        await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        meter_reading._to_dict.assert_called_once()
        client._make_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_returns_none(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=Decimal("123.45"))

        # Act
        result = await resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        assert result is None


class TestMeterReadingResourceList:
    """Tests for MeterReadingResource.list method."""

    @pytest.mark.asyncio
    async def test_list_without_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value=[
                {
                    "timestamp": "2024-01-15T10:00:00.000Z",
                    "value": "123.45",
                    "rolloverOffset": 0,
                    "meterId": "meter-abc",
                    "note": None,
                    "meterNumber": None,
                }
            ]
        )
        resource = MeterReadingResource(client)

        # Act
        result = await resource.list(device_id="device-123")

        # Assert
        assert len(result) == 1
        assert str(result[0].value) == "123.45"
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            params=None,
        )

    @pytest.mark.asyncio
    async def test_list_with_all_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = MeterReadingResource(client)
        from_ts = datetime(2024, 1, 1)
        to_ts = datetime(2024, 12, 31)

        # Act
        await resource.list(
            device_id="device-123",
            meter_id="meter-abc",
            from_timestamp=from_ts,
            to_timestamp=to_ts,
            sort=SortDirection.ASC,
        )

        # Assert
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            params={
                "meterId": "meter-abc",
                "from": "2024-01-01T00:00:00.000",
                "to": "2024-12-31T00:00:00.000",
                "sort": "asc",
            },
        )

    @pytest.mark.asyncio
    async def test_list_default_sort_desc_not_sent(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=[])
        resource = MeterReadingResource(client)

        # Act
        await resource.list(device_id="device-123", sort=SortDirection.DESC)

        # Assert
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            params=None,
        )


class TestMeterReadingResourceDelete:
    """Tests for MeterReadingResource.delete method."""

    @pytest.mark.asyncio
    async def test_delete(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)

        # Act
        await resource.delete(device_id="device-123", timestamp=timestamp)

        # Assert
        client._make_request.assert_called_once_with(
            method="DELETE",
            endpoint="/v3/devices/standard/device-123/meter-readings",
            json={"timestamp": "2024-01-15T10:30:45.123"},
        )

    @pytest.mark.asyncio
    async def test_delete_returns_none(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock()
        resource = MeterReadingResource(client)
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)

        # Act
        result = await resource.delete(device_id="device-123", timestamp=timestamp)

        # Assert
        assert result is None


class TestMeterReadingResourceExport:
    """Tests for MeterReadingResource.export method."""

    @pytest.mark.asyncio
    async def test_export_minimal(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=b"date,value\n2024-01-15,123.45\n")
        resource = MeterReadingResource(client)
        config = ExportMeterReadingsDto(columns=[ExportColumn.DATE, ExportColumn.VALUE])

        # Act
        result = await resource.export(device_id="device-123", export_config=config)

        # Assert
        assert result == b"date,value\n2024-01-15,123.45\n"
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings/export",
            json={
                "columns": ["date", "value"],
                "includeHeader": True,
                "delimiter": "comma",
                "dateFormat": "iso",
            },
            params=None,
        )

    @pytest.mark.asyncio
    async def test_export_with_filters(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(return_value=b"csv-data")
        resource = MeterReadingResource(client)
        config = ExportMeterReadingsDto(columns=[ExportColumn.DATE, ExportColumn.VALUE])
        from_ts = datetime(2024, 1, 1)

        # Act
        await resource.export(
            device_id="device-123",
            export_config=config,
            meter_id="meter-abc",
            from_timestamp=from_ts,
            sort=SortDirection.ASC,
        )

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v3/devices/standard/device-123/meter-readings/export",
            json={
                "columns": ["date", "value"],
                "includeHeader": True,
                "delimiter": "comma",
                "dateFormat": "iso",
            },
            params={
                "meterId": "meter-abc",
                "from": "2024-01-01T00:00:00.000",
                "sort": "asc",
            },
        )
