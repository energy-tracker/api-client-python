"""Tests for Energy Tracker API exceptions."""

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


class TestEnergyTrackerAPIError:
    """Tests for base EnergyTrackerAPIError."""

    def test_initialization_with_message(self):
        # Arrange
        message = "An error occurred"

        # Act
        error = EnergyTrackerAPIError(message)

        # Assert
        assert str(error) == message
        assert error.api_message == []

    def test_initialization_with_api_message(self):
        # Arrange
        message = "An error occurred"
        api_message = ["Field is required", "Invalid format"]

        # Act
        error = EnergyTrackerAPIError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message

    def test_initialization_with_empty_api_message(self):
        # Arrange
        message = "An error occurred"

        # Act
        error = EnergyTrackerAPIError(message, api_message=[])

        # Assert
        assert str(error) == message
        assert error.api_message == []

    def test_is_exception(self):
        # Arrange
        error = EnergyTrackerAPIError("Error")

        # Act & Assert
        assert isinstance(error, Exception)


class TestValidationError:
    """Tests for ValidationError (HTTP 400)."""

    def test_initialization(self):
        # Arrange
        message = "Invalid input"
        api_message = ["Field 'value' is required"]

        # Act
        error = ValidationError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message

    def test_inherits_from_base_error(self):
        # Arrange
        error = ValidationError("Invalid input")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)
        assert isinstance(error, Exception)

    def test_default_api_message(self):
        # Arrange & Act
        error = ValidationError("Invalid input")

        # Assert
        assert error.api_message == []


class TestAuthenticationError:
    """Tests for AuthenticationError (HTTP 401)."""

    def test_initialization(self):
        # Arrange
        message = "Invalid access token"
        api_message = ["Token expired"]

        # Act
        error = AuthenticationError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message

    def test_inherits_from_base_error(self):
        # Arrange
        error = AuthenticationError("Unauthorized")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_default_api_message(self):
        # Arrange & Act
        error = AuthenticationError("Unauthorized")

        # Assert
        assert error.api_message == []


class TestForbiddenError:
    """Tests for ForbiddenError (HTTP 403)."""

    def test_initialization(self):
        # Arrange
        message = "Access forbidden"
        api_message = ["Insufficient scopes"]

        # Act
        error = ForbiddenError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message

    def test_inherits_from_base_error(self):
        # Arrange
        error = ForbiddenError("Forbidden")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_default_api_message(self):
        # Arrange & Act
        error = ForbiddenError("Forbidden")

        # Assert
        assert error.api_message == []


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError (HTTP 404)."""

    def test_initialization(self):
        # Arrange
        message = "Resource not found"
        api_message = ["No valid meter available"]

        # Act
        error = ResourceNotFoundError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message

    def test_inherits_from_base_error(self):
        # Arrange
        error = ResourceNotFoundError("Not found")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_default_api_message(self):
        # Arrange & Act
        error = ResourceNotFoundError("Not found")

        # Assert
        assert error.api_message == []


class TestConflictError:
    """Tests for ConflictError (HTTP 409)."""

    def test_initialization(self):
        # Arrange
        message = "Conflict occurred"
        api_message = ["Meter reading already exists"]

        # Act
        error = ConflictError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message

    def test_inherits_from_base_error(self):
        # Arrange
        error = ConflictError("Conflict")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_default_api_message(self):
        # Arrange & Act
        error = ConflictError("Conflict")

        # Assert
        assert error.api_message == []


class TestRateLimitError:
    """Tests for RateLimitError (HTTP 429)."""

    def test_initialization_with_retry_after(self):
        # Arrange
        message = "Rate limit exceeded"
        api_message = ["Too many requests"]
        retry_after = 60

        # Act
        error = RateLimitError(message, api_message=api_message, retry_after=retry_after)

        # Assert
        assert str(error) == message
        assert error.api_message == api_message
        assert error.retry_after == 60

    def test_initialization_without_retry_after(self):
        # Arrange
        message = "Rate limit exceeded"

        # Act
        error = RateLimitError(message)

        # Assert
        assert str(error) == message
        assert error.api_message == []
        assert error.retry_after is None

    def test_inherits_from_base_error(self):
        # Arrange
        error = RateLimitError("Rate limit exceeded")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_retry_after_none_by_default(self):
        # Arrange & Act
        error = RateLimitError("Rate limit exceeded", api_message=["Try again later"])

        # Assert
        assert error.retry_after is None

    def test_retry_after_with_zero(self):
        # Arrange & Act
        error = RateLimitError("Rate limit exceeded", retry_after=0)

        # Assert
        assert error.retry_after == 0


class TestNetworkError:
    """Tests for NetworkError (network/connection issues)."""

    def test_initialization(self):
        # Arrange
        message = "Connection refused"

        # Act
        error = NetworkError(message)

        # Assert
        assert str(error) == message
        assert error.api_message == []

    def test_inherits_from_base_error(self):
        # Arrange
        error = NetworkError("Connection failed")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_initialization_with_api_message(self):
        # Arrange
        message = "Network error"
        api_message = []

        # Act
        error = NetworkError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == []


class TestTimeoutError:
    """Tests for TimeoutError (request timeout)."""

    def test_initialization(self):
        # Arrange
        message = "Request timeout after 30 seconds"

        # Act
        error = TimeoutError(message)

        # Assert
        assert str(error) == message
        assert error.api_message == []

    def test_inherits_from_base_error(self):
        # Arrange
        error = TimeoutError("Timeout")

        # Act & Assert
        assert isinstance(error, EnergyTrackerAPIError)

    def test_initialization_with_api_message(self):
        # Arrange
        message = "Operation timed out"
        api_message = []

        # Act
        error = TimeoutError(message, api_message=api_message)

        # Assert
        assert str(error) == message
        assert error.api_message == []
