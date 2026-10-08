"""Tests for Energy Tracker API token resources."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.exceptions import EnergyTrackerAPIError
from energy_tracker_api.resources.token import TokenResource


class TestTokenResourceInitialization:
    """Tests for TokenResource initialization."""

    def test_initialization(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)

        # Act
        resource = TokenResource(client)

        # Assert
        assert resource._client == client


class TestTokenResourceStatus:
    """Tests for TokenResource.status method."""

    @pytest.mark.asyncio
    async def test_status_with_expiry(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value={
                "displayName": "Home Assistant",
                "scopes": ["write:meter-reading", "read:measuring-device"],
                "expiresAt": "2027-01-01T00:00:00.000Z",
            }
        )
        resource = TokenResource(client)

        # Act
        result = await resource.status()

        # Assert
        assert result.display_name == "Home Assistant"
        assert result.scopes == ["write:meter-reading", "read:measuring-device"]
        assert result.expires_at == datetime(2027, 1, 1, tzinfo=UTC)
        client._make_request.assert_called_once_with(
            method="GET",
            endpoint="/v1/token/status",
        )

    @pytest.mark.asyncio
    async def test_status_without_expiry(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value={
                "displayName": "Write only",
                "scopes": ["write:meter-reading"],
                "expiresAt": None,
            }
        )
        resource = TokenResource(client)

        # Act
        result = await resource.status()

        # Assert
        assert result.display_name == "Write only"
        assert result.expires_at is None

    @pytest.mark.asyncio
    async def test_status_with_invalid_scopes_raises_api_error(self):
        # Arrange
        client = Mock(spec=EnergyTrackerClient)
        client._make_request = AsyncMock(
            return_value={
                "displayName": "Home Assistant",
                "scopes": "write:meter-reading",
                "expiresAt": None,
            }
        )
        resource = TokenResource(client)

        # Act & Assert
        with pytest.raises(EnergyTrackerAPIError) as exc_info:
            await resource.status()

        assert str(exc_info.value) == "Invalid TokenStatusDto response"
