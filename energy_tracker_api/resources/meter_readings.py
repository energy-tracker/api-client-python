"""Meter reading resource handlers for Energy Tracker API."""

from datetime import datetime

from ..exceptions import EnergyTrackerAPIError
from ..models import (
    CreateMeterReadingDto,
    ExportMeterReadingsDto,
    MeterReadingDto,
    SortDirection,
    TimestampDto,
)
from .base import BaseResource


class MeterReadingResource(BaseResource):
    """Handler for meter reading operations."""

    async def list(
        self,
        device_id: str,
        *,
        meter_id: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        sort: SortDirection = SortDirection.DESC,
    ) -> list[MeterReadingDto]:
        """Returns meter readings for the specified device.

        Args:
            device_id: Unique identifier of the measuring device.
            meter_id: Filter by meter ID.
            from_timestamp: Only include readings at or after this timestamp.
            to_timestamp: Only include readings at or before this timestamp.
            sort: Sort direction (default: descending by timestamp).

        Returns:
            List of meter readings, ordered chronologically.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If query parameters are invalid.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        params: dict[str, str] = {}
        if meter_id is not None:
            params["meterId"] = meter_id
        if from_timestamp is not None:
            params["from"] = from_timestamp.isoformat(timespec="milliseconds")
        if to_timestamp is not None:
            params["to"] = to_timestamp.isoformat(timespec="milliseconds")
        if sort != SortDirection.DESC:
            params["sort"] = sort.value

        return await self._request_model_list(
            response_type=MeterReadingDto,
            method="GET",
            endpoint=f"/v3/devices/standard/{device_id}/meter-readings",
            params=params or None,
        )

    async def create(
        self,
        device_id: str,
        meter_reading: CreateMeterReadingDto,
        allow_rounding: bool | None = None,
    ) -> None:
        """Create a new meter reading for the specified device.

        Args:
            device_id: Unique identifier of the measuring device.
            meter_reading: Meter reading data to submit.
            allow_rounding: Optional flag to allow rounding of the meter value.
                When true, the value may be rounded according to meter precision.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions for the device.
            ValidationError: If input data is invalid.
            ResourceNotFoundError: If no valid meter is available for the timestamp.
            ConflictError: If a meter reading already exists for the given timestamp.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        endpoint = f"/v3/devices/standard/{device_id}/meter-readings"

        params = {}
        if allow_rounding is not None:
            params["allowRounding"] = str(allow_rounding).lower()

        await self._client._make_request(
            method="POST",
            endpoint=endpoint,
            json=meter_reading._to_dict(),
            params=params or None,
        )

    async def delete(
        self,
        device_id: str,
        timestamp: datetime,
    ) -> None:
        """Delete a meter reading for the specified device and timestamp.

        Args:
            device_id: Unique identifier of the measuring device.
            timestamp: Timestamp of the reading to delete.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If input data is invalid.
            ResourceNotFoundError: If no matching reading found for given timestamp.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        ts_dto = TimestampDto(timestamp=timestamp)

        await self._client._make_request(
            method="DELETE",
            endpoint=f"/v3/devices/standard/{device_id}/meter-readings",
            json=ts_dto._to_dict(),
        )

    async def export(
        self,
        device_id: str,
        export_config: ExportMeterReadingsDto,
        *,
        meter_id: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        sort: SortDirection = SortDirection.DESC,
    ) -> bytes:
        """Export meter readings as CSV.

        Args:
            device_id: Unique identifier of the measuring device.
            export_config: Export configuration (columns, delimiter, etc.).
            meter_id: Filter by meter ID.
            from_timestamp: Only include readings at or after this timestamp.
            to_timestamp: Only include readings at or before this timestamp.
            sort: Sort direction (default: descending by timestamp).

        Returns:
            CSV file content as bytes.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If input data or query parameters are invalid.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        params: dict[str, str] = {}
        if meter_id is not None:
            params["meterId"] = meter_id
        if from_timestamp is not None:
            params["from"] = from_timestamp.isoformat(timespec="milliseconds")
        if to_timestamp is not None:
            params["to"] = to_timestamp.isoformat(timespec="milliseconds")
        if sort != SortDirection.DESC:
            params["sort"] = sort.value

        data = await self._client._make_request(
            method="POST",
            endpoint=f"/v3/devices/standard/{device_id}/meter-readings/export",
            json=export_config._to_dict(),
            params=params or None,
        )
        if not isinstance(data, bytes):
            raise EnergyTrackerAPIError(f"Expected bytes response, got {type(data).__name__}")
        return data
