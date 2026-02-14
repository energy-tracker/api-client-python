"""Exceptions for Energy Tracker API client."""


class EnergyTrackerAPIError(Exception):
    """Base exception for Energy Tracker API errors.

    Attributes:
        api_message: List of messages from the API response body.
    """

    def __init__(self, message: str, api_message: list[str] | None = None):
        super().__init__(message)
        self.api_message = api_message if api_message is not None else []


class ValidationError(EnergyTrackerAPIError):
    """Raised when input validation fails (HTTP 400).

    Attributes:
        api_message: List of messages from the API response body.
    """

    pass


class AuthenticationError(EnergyTrackerAPIError):
    """Raised when authentication fails (HTTP 401).

    Attributes:
        api_message: List of messages from the API response body.
    """

    pass


class ForbiddenError(EnergyTrackerAPIError):
    """Raised when access is forbidden (HTTP 403).

    Attributes:
        api_message: List of messages from the API response body.
    """

    pass


class ResourceNotFoundError(EnergyTrackerAPIError):
    """Raised when a resource is not found (HTTP 404).

    Attributes:
        api_message: List of messages from the API response body.
    """

    pass


class ConflictError(EnergyTrackerAPIError):
    """Raised when a conflict occurs (HTTP 409).

    Attributes:
        api_message: List of messages from the API response body.
    """

    pass


class RateLimitError(EnergyTrackerAPIError):
    """Raised when rate limit is exceeded (HTTP 429).

    Attributes:
        api_message: List of messages from the API response body.
        retry_after: Optional number of seconds to wait before retrying.
    """

    def __init__(
        self, message: str, api_message: list[str] | None = None, retry_after: int | None = None
    ):
        super().__init__(message, api_message)
        self.retry_after = retry_after


class NetworkError(EnergyTrackerAPIError):
    """Raised when a network error occurs (connection issues, DNS, etc.).

    Attributes:
        api_message: List of messages from the API response body (always empty for network errors).
    """

    pass


class TimeoutError(EnergyTrackerAPIError):
    """Raised when a request times out.

    Attributes:
        api_message: List of messages from the API response body (always empty for timeout errors).
    """

    pass
