"""Device resource handlers for Energy Tracker API."""

from datetime import datetime

from ..models import DeviceSummaryDto
from .base import BaseResource


class DeviceResource(BaseResource):
    """Handler for device operations."""

    async def list_standard(
        self,
        *,
        name: str | None = None,
        folder_path: str | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
    ) -> list[DeviceSummaryDto]:
        """Returns all standard measuring devices.

        Args:
            name: Filter by (partial) device name.
            folder_path: Filter by folder path.
            updated_after: Include only devices updated at or after this timestamp.
            updated_before: Include only devices updated at or before this timestamp.

        Returns:
            List of standard device summaries.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If query parameters are invalid.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        params: dict[str, str] = {}
        if name is not None:
            params["name"] = name
        if folder_path is not None:
            params["folderPath"] = folder_path
        if updated_after is not None:
            params["updatedAfter"] = updated_after.isoformat(timespec="milliseconds")
        if updated_before is not None:
            params["updatedBefore"] = updated_before.isoformat(timespec="milliseconds")

        return await self._request_model_list(
            response_type=DeviceSummaryDto,
            method="GET",
            endpoint="/v1/devices/standard",
            params=params or None,
        )

    async def list_virtual(
        self,
        *,
        name: str | None = None,
        folder_path: str | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
    ) -> list[DeviceSummaryDto]:
        """Returns all virtual measuring devices.

        Args:
            name: Filter by (partial) device name.
            folder_path: Filter by folder path.
            updated_after: Include only devices updated at or after this timestamp.
            updated_before: Include only devices updated at or before this timestamp.

        Returns:
            List of virtual device summaries.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If query parameters are invalid.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        params: dict[str, str] = {}
        if name is not None:
            params["name"] = name
        if folder_path is not None:
            params["folderPath"] = folder_path
        if updated_after is not None:
            params["updatedAfter"] = updated_after.isoformat(timespec="milliseconds")
        if updated_before is not None:
            params["updatedBefore"] = updated_before.isoformat(timespec="milliseconds")

        return await self._request_model_list(
            response_type=DeviceSummaryDto,
            method="GET",
            endpoint="/v1/devices/virtual",
            params=params or None,
        )
