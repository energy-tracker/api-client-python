"""Environment record resource handlers for Energy Tracker API."""

from datetime import datetime

from ..models import (
    CreateEnvironmentEntryDto,
    CreateEnvironmentRecordDto,
    EnvironmentRecordDto,
    TimestampDto,
)
from .base import BaseResource


class EnvironmentResource(BaseResource):
    """Handler for environment record operations."""

    async def list(
        self,
        device_id: str,
    ) -> list[EnvironmentRecordDto]:
        """Returns all environment records for the specified device.

        Args:
            device_id: Unique identifier of the measuring device.

        Returns:
            List of environment records, sorted alphabetically by title.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ResourceNotFoundError: If the device does not exist or is not accessible.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        return await self._request_model_list(
            response_type=EnvironmentRecordDto,
            method="GET",
            endpoint=f"/v1/devices/standard/{device_id}/environments",
        )

    async def get(
        self,
        device_id: str,
        environment_id: str,
    ) -> EnvironmentRecordDto:
        """Returns a specific environment record.

        Args:
            device_id: Unique identifier of the measuring device.
            environment_id: Unique identifier of the environment record.

        Returns:
            The environment record with its entries.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ResourceNotFoundError: If the resource does not exist or is not accessible.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        return await self._request_model(
            response_type=EnvironmentRecordDto,
            method="GET",
            endpoint=f"/v1/devices/standard/{device_id}/environments/{environment_id}",
        )

    async def create(
        self,
        device_id: str,
        environment_record: CreateEnvironmentRecordDto,
    ) -> EnvironmentRecordDto:
        """Creates a new environment record for the specified device.

        Args:
            device_id: Unique identifier of the measuring device.
            environment_record: Environment record data to create.

        Returns:
            The newly created environment record.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If input data is invalid.
            ResourceNotFoundError: If the device does not exist or is not accessible.
            ConflictError: If an environment record with the same name and unit already exists.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        return await self._request_model(
            response_type=EnvironmentRecordDto,
            method="POST",
            endpoint=f"/v1/devices/standard/{device_id}/environments",
            json=environment_record._to_dict(),
        )

    async def delete(
        self,
        device_id: str,
        environment_id: str,
    ) -> None:
        """Deletes an environment record for the specified device.

        Args:
            device_id: Unique identifier of the measuring device.
            environment_id: Unique identifier of the environment record.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ResourceNotFoundError: If no matching environment record found.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        await self._client._make_request(
            method="DELETE",
            endpoint=f"/v1/devices/standard/{device_id}/environments/{environment_id}",
        )

    async def create_entry(
        self,
        device_id: str,
        environment_id: str,
        entry: CreateEnvironmentEntryDto,
    ) -> None:
        """Creates a new measurement entry for the specified environment record.

        Args:
            device_id: Unique identifier of the measuring device.
            environment_id: Unique identifier of the environment record.
            entry: Environment entry data to create.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ValidationError: If input data is invalid.
            ResourceNotFoundError: If the device or environment record does not exist.
            ConflictError: If an entry with the same timestamp already exists.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        await self._client._make_request(
            method="POST",
            endpoint=f"/v1/devices/standard/{device_id}/environments/{environment_id}",
            json=entry._to_dict(),
        )

    async def delete_entry(
        self,
        device_id: str,
        environment_id: str,
        timestamp: datetime,
    ) -> None:
        """Deletes an environment entry by timestamp.

        Args:
            device_id: Unique identifier of the measuring device.
            environment_id: Unique identifier of the environment record.
            timestamp: Timestamp of the entry to delete.

        Raises:
            AuthenticationError: If authentication fails.
            ForbiddenError: If insufficient permissions.
            ResourceNotFoundError: If no matching entry found for given timestamp.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        ts_dto = TimestampDto(timestamp=timestamp)

        await self._client._make_request(
            method="DELETE",
            endpoint=f"/v1/devices/standard/{device_id}/environments/{environment_id}/entries",
            json=ts_dto._to_dict(),
        )
