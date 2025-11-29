"""Tests for Energy Tracker API resources."""

from datetime import datetime
from unittest.mock import Mock

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.models import CreateMeterReadingDto
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

    def test_create_with_minimal_data(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=123.45)

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={"value": 123.45},
            params=None,
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_timestamp(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        meter_reading = CreateMeterReadingDto(value=123.45, timestamp=timestamp)

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={"value": 123.45, "timestamp": "2024-01-15T10:30:45.123"},
            params=None,
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_note(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=123.45, note="Manual reading")

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={"value": 123.45, "note": "Manual reading"},
            params=None,
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_all_fields(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        timestamp = datetime(2024, 1, 15, 10, 30, 45, 123000)
        meter_reading = CreateMeterReadingDto(
            value=123.45, timestamp=timestamp, note="Manual reading"
        )

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={
                "value": 123.45,
                "timestamp": "2024-01-15T10:30:45.123",
                "note": "Manual reading",
            },
            params=None,
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_allow_rounding_true(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=123.45)

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading, allow_rounding=True)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={"value": 123.45},
            params={"allowRounding": "true"},
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_allow_rounding_false(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=123.45)

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading, allow_rounding=False)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={"value": 123.45},
            params={"allowRounding": "false"},
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_allow_rounding_none(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=123.45)

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading, allow_rounding=None)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/device-123/meter-readings",
            json={"value": 123.45},
            params=None,
            headers={"Content-Type": "application/json"},
        )

    def test_create_with_different_device_id(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "another-device-456"
        meter_reading = CreateMeterReadingDto(value=999.99)

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/devices/standard/another-device-456/meter-readings",
            json={"value": 999.99},
            params=None,
            headers={"Content-Type": "application/json"},
        )

    def test_create_calls_to_dict_on_meter_reading(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = Mock(spec=CreateMeterReadingDto)
        meter_reading._to_dict.return_value = {"value": 100.0}

        # Act
        resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        meter_reading._to_dict.assert_called_once()
        client._make_request.assert_called_once()

    def test_create_returns_none(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        resource = MeterReadingResource(client)
        device_id = "device-123"
        meter_reading = CreateMeterReadingDto(value=123.45)

        # Act
        result = resource.create(device_id=device_id, meter_reading=meter_reading)

        # Assert
        assert result is None
