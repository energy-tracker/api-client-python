"""Tests for Energy Tracker API client."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.exceptions import (
    AuthenticationError,
    ConflictError,
    EnergyTrackerAPIError,
    ForbiddenError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)


class TestEnergyTrackerClientInitialization:
    """Tests for EnergyTrackerClient initialization."""

    def test_initialization_with_defaults(self):
        # Arrange
        access_token = "test-token"

        # Act
        client = EnergyTrackerClient(access_token=access_token)

        # Assert
        assert client._access_token == access_token
        assert client._base_url == "https://public-api.energy-tracker.best-ios-apps.de"
        assert client._timeout.total == 10
        assert client._session is None

    def test_initialization_with_custom_base_url(self):
        # Arrange
        access_token = "test-token"
        custom_url = "https://custom-api.example.com"

        # Act
        client = EnergyTrackerClient(access_token=access_token, base_url=custom_url)

        # Assert
        assert client._base_url == custom_url

    def test_initialization_with_custom_timeout(self):
        # Arrange
        access_token = "test-token"
        custom_timeout = 30

        # Act
        client = EnergyTrackerClient(access_token=access_token, timeout=custom_timeout)

        # Assert
        assert client._timeout.total == 30

    def test_base_url_normalization_strips_whitespace(self):
        # Arrange
        access_token = "test-token"
        url_with_whitespace = "  https://api.example.com  "

        # Act
        client = EnergyTrackerClient(access_token=access_token, base_url=url_with_whitespace)

        # Assert
        assert client._base_url == "https://api.example.com"

    def test_base_url_normalization_removes_trailing_slash(self):
        # Arrange
        access_token = "test-token"
        url_with_slash = "https://api.example.com/"

        # Act
        client = EnergyTrackerClient(access_token=access_token, base_url=url_with_slash)

        # Assert
        assert client._base_url == "https://api.example.com"

    def test_base_url_normalization_combined(self):
        # Arrange
        access_token = "test-token"
        messy_url = "  https://api.example.com/  "

        # Act
        client = EnergyTrackerClient(access_token=access_token, base_url=messy_url)

        # Assert
        assert client._base_url == "https://api.example.com"

    def test_meter_readings_resource_is_initialized(self):
        # Arrange
        access_token = "test-token"

        # Act
        client = EnergyTrackerClient(access_token=access_token)

        # Assert
        assert client.meter_readings is not None
        assert hasattr(client.meter_readings, "create")


class TestEnergyTrackerClientExtractApiMessage:
    """Tests for _extract_api_message method."""

    def test_extract_api_message_with_list(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        data = {"message": ["Error 1", "Error 2"]}

        # Act
        result = client._extract_api_message(data)

        # Assert
        assert result == ["Error 1", "Error 2"]

    def test_extract_api_message_with_string(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        data = {"message": "Single error message"}

        # Act
        result = client._extract_api_message(data)

        # Assert
        assert result == ["Single error message"]

    def test_extract_api_message_with_no_message(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        data = {}

        # Act
        result = client._extract_api_message(data)

        # Assert
        assert result == []

    def test_extract_api_message_with_non_string_list_items(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        data = {"message": [123, 456]}

        # Act
        result = client._extract_api_message(data)

        # Assert
        assert result == ["123", "456"]


class TestEnergyTrackerClientMakeRequest:
    """Tests for _make_request method."""

    @pytest.mark.asyncio
    async def test_successful_request(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act
            response = await client._make_request("GET", "/v1/test")

            # Assert
            assert response.status == 200
            mock_session.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_validation_error_400_without_api_message(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                await client._make_request("POST", "/v1/test")

            assert str(exc_info.value) == "Bad Request"
            assert exc_info.value.api_message == []

    @pytest.mark.asyncio
    async def test_validation_error_400_with_api_message(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(
            return_value={"message": ["Field 'value' is required", "Field 'timestamp' is invalid"]}
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                await client._make_request("POST", "/v1/test")

            assert (
                str(exc_info.value)
                == "Bad Request (Field 'value' is required; Field 'timestamp' is invalid)"
            )
            assert exc_info.value.api_message == [
                "Field 'value' is required",
                "Field 'timestamp' is invalid",
            ]

    @pytest.mark.asyncio
    async def test_authentication_error_401(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.json = AsyncMock(return_value={"message": "Invalid token"})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Unauthorized: Check your access token"
            assert exc_info.value.api_message == ["Invalid token"]

    @pytest.mark.asyncio
    async def test_forbidden_error_403(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(ForbiddenError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Forbidden: Insufficient permissions"

    @pytest.mark.asyncio
    async def test_resource_not_found_error_404(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(ResourceNotFoundError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Not Found"

    @pytest.mark.asyncio
    async def test_conflict_error_409(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 409
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(ConflictError) as exc_info:
                await client._make_request("POST", "/v1/test")

            assert str(exc_info.value) == "Conflict"

    @pytest.mark.asyncio
    async def test_rate_limit_error_429_without_retry_after(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.headers = {}
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(RateLimitError) as exc_info:
                await client._make_request("POST", "/v1/test")

            assert str(exc_info.value) == "Too Many Requests: Rate limit exceeded"
            assert exc_info.value.retry_after is None

    @pytest.mark.asyncio
    async def test_rate_limit_error_429_with_retry_after(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(RateLimitError) as exc_info:
                await client._make_request("POST", "/v1/test")

            assert (
                str(exc_info.value)
                == "Too Many Requests: Rate limit exceeded - Retry after 60 seconds"
            )
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_server_error_500(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Server error: 500"

    @pytest.mark.asyncio
    async def test_server_error_503(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 503
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Server error: 503"

    @pytest.mark.asyncio
    async def test_unknown_client_error_4xx(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        mock_response = AsyncMock()
        mock_response.status = 418  # I'm a teapot
        mock_response.json = AsyncMock(return_value={})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(return_value=mock_response)
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "HTTP error: 418"

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token", timeout=5)

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(side_effect=asyncio.TimeoutError())
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(TimeoutError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Request timeout after 5 seconds"

    @pytest.mark.asyncio
    async def test_network_error(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.request = Mock(side_effect=aiohttp.ClientError("Connection error"))
            mock_get_session.return_value = mock_session

            # Act & Assert
            with pytest.raises(NetworkError) as exc_info:
                await client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Request failed: Connection error"


class TestEnergyTrackerClientContextManager:
    """Tests for async context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_enter(self):
        # Arrange
        access_token = "test-token"

        # Act
        async with EnergyTrackerClient(access_token=access_token) as client:
            # Assert
            assert client._access_token == access_token
            assert isinstance(client, EnergyTrackerClient)

    @pytest.mark.asyncio
    async def test_context_manager_exit_closes_session(self):
        # Arrange
        access_token = "test-token"
        client = EnergyTrackerClient(access_token=access_token)

        # Create a mock session
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.closed = False
        mock_session.close = AsyncMock()
        client._session = mock_session

        # Act
        async with client:
            pass

        # Assert
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_method(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")

        # Create a mock session
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.closed = False
        mock_session.close = AsyncMock()
        client._session = mock_session

        # Act
        await client.close()

        # Assert
        mock_session.close.assert_called_once()
