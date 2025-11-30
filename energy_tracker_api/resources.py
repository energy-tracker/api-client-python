"""Resource handlers for Energy Tracker API."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import EnergyTrackerClient

from .models import CreateMeterReadingDto


class MeterReadingResource:
    """Handler for meter reading operations."""

    def __init__(self, client: "EnergyTrackerClient"):
        self._client = client

    async def create(
        self,
        device_id: str,
        meter_reading: CreateMeterReadingDto,
        allow_rounding: Optional[bool] = None,
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
        endpoint = f"/v1/devices/standard/{device_id}/meter-readings"

        params = {}
        if allow_rounding is not None:
            params["allowRounding"] = str(allow_rounding).lower()

        headers = {"Content-Type": "application/json"}

        await self._client._make_request(
            method="POST",
            endpoint=endpoint,
            json=meter_reading._to_dict(),
            params=params if params else None,
            headers=headers,
        )
