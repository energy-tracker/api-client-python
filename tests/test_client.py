"""Tests for Energy Tracker API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from energy_tracker_api.client import EnergyTrackerClient
from energy_tracker_api.exceptions import (
    AuthenticationError,
    ConflictError,
    EnergyTrackerAPIError,
    ForbiddenError,
    RateLimitError,
    ResourceNotFoundError,
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
        assert client._timeout == 10
        assert client._session.headers["Authorization"] == "Bearer test-token"

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
        assert client._timeout == 30

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
        response = Mock()
        response.json.return_value = {"message": ["Error 1", "Error 2"]}

        # Act
        result = client._extract_api_message(response)

        # Assert
        assert result == ["Error 1", "Error 2"]

    def test_extract_api_message_with_string(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        response = Mock()
        response.json.return_value = {"message": "Single error message"}

        # Act
        result = client._extract_api_message(response)

        # Assert
        assert result == ["Single error message"]

    def test_extract_api_message_with_no_message(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        response = Mock()
        response.json.return_value = {}

        # Act
        result = client._extract_api_message(response)

        # Assert
        assert result == []

    def test_extract_api_message_with_invalid_json(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        response = Mock()
        response.json.side_effect = ValueError("Invalid JSON")

        # Act
        result = client._extract_api_message(response)

        # Assert
        assert result == []

    def test_extract_api_message_with_non_string_list_items(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        response = Mock()
        response.json.return_value = {"message": [123, 456]}

        # Act
        result = client._extract_api_message(response)

        # Assert
        assert result == ["123", "456"]


class TestEnergyTrackerClientMakeRequest:
    """Tests for _make_request method."""

    def test_successful_request(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act
            response = client._make_request("GET", "/v1/test")

            # Assert
            assert response.status_code == 200
            mock_request.assert_called_once_with(
                method="GET",
                url="https://public-api.energy-tracker.best-ios-apps.de/v1/test",
                timeout=10,
            )

    def test_validation_error_400_without_api_message(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                client._make_request("POST", "/v1/test")

            assert str(exc_info.value) == "Bad Request"
            assert exc_info.value.api_message == []

    def test_validation_error_400_with_api_message(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "message": ["Field 'value' is required", "Field 'timestamp' is invalid"]
            }
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                client._make_request("POST", "/v1/test")

            assert (
                str(exc_info.value)
                == "Bad Request (Field 'value' is required; Field 'timestamp' is invalid)"
            )
            assert exc_info.value.api_message == [
                "Field 'value' is required",
                "Field 'timestamp' is invalid",
            ]

    def test_authentication_error_401(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Invalid token"}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Unauthorized: Check your access token"
            assert exc_info.value.api_message == ["Invalid token"]

    def test_forbidden_error_403(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(ForbiddenError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Forbidden: Insufficient permissions"

    def test_resource_not_found_error_404(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(ResourceNotFoundError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Not Found"

    def test_conflict_error_409(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 409
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(ConflictError) as exc_info:
                client._make_request("POST", "/v1/test")

            assert str(exc_info.value) == "Conflict"

    def test_rate_limit_error_429_without_retry_after(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {}
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(RateLimitError) as exc_info:
                client._make_request("POST", "/v1/test")

            assert str(exc_info.value) == "Too Many Requests: Rate limit exceeded"
            assert exc_info.value.retry_after is None

    def test_rate_limit_error_429_with_retry_after(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(RateLimitError) as exc_info:
                client._make_request("POST", "/v1/test")

            assert (
                str(exc_info.value)
                == "Too Many Requests: Rate limit exceeded - Retry after 60 seconds"
            )
            assert exc_info.value.retry_after == 60

    def test_server_error_500(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Server error: 500"

    def test_server_error_503(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Server error: 503"

    def test_unknown_client_error_4xx(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 418  # I'm a teapot
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "HTTP error: 418"

    def test_timeout_error(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token", timeout=5)
        with patch.object(client._session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.Timeout()

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Request timeout after 5 seconds"

    def test_request_exception(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")
        with patch.object(client._session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.RequestException("Connection error")

            # Act & Assert
            with pytest.raises(EnergyTrackerAPIError) as exc_info:
                client._make_request("GET", "/v1/test")

            assert str(exc_info.value) == "Request failed: Connection error"


class TestEnergyTrackerClientContextManager:
    """Tests for context manager functionality."""

    def test_context_manager_enter(self):
        # Arrange
        access_token = "test-token"

        # Act
        with EnergyTrackerClient(access_token=access_token) as client:
            # Assert
            assert client._access_token == access_token
            assert isinstance(client, EnergyTrackerClient)

    def test_context_manager_exit_closes_session(self):
        # Arrange
        access_token = "test-token"
        client = EnergyTrackerClient(access_token=access_token)

        with patch.object(client._session, "close") as mock_close:
            # Act
            with client:
                pass

            # Assert
            mock_close.assert_called_once()

    def test_close_method(self):
        # Arrange
        client = EnergyTrackerClient(access_token="test-token")

        with patch.object(client._session, "close") as mock_close:
            # Act
            client.close()

            # Assert
            mock_close.assert_called_once()
