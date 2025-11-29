"""Energy Tracker API client implementation."""

from typing import Any, Optional
from urllib.parse import urljoin

import requests

from .exceptions import (
    AuthenticationError,
    ConflictError,
    EnergyTrackerAPIError,
    ForbiddenError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
)


class EnergyTrackerClient:
    """Client for interacting with the Energy Tracker public REST API."""

    _DEFAULT_BASE_URL = "https://public-api.energy-tracker.best-ios-apps.de"

    def __init__(
        self,
        access_token: str,
        base_url: Optional[str] = None,
        timeout: int = 10,
    ):
        """Initialize the Energy Tracker API client.

        Args:
            access_token: Bearer token for authentication.
            base_url: Base URL of the API (defaults to production API).
            timeout: Request timeout in seconds (default: 10).
        """
        url = base_url or self._DEFAULT_BASE_URL

        self._base_url = url.strip().rstrip("/")
        self._access_token = access_token
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {access_token}"})

        from .resources import MeterReadingResource

        self.meter_readings = MeterReadingResource(self)

    def _extract_api_message(self, response: requests.Response) -> list[str]:
        try:
            data = response.json()
            message = data.get("message")

            if isinstance(message, list):
                return [str(m) for m in message]
            elif isinstance(message, str):
                return [message]
            else:
                return []
        except (ValueError, KeyError):
            return []

    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        url = urljoin(self._base_url, endpoint)

        try:
            response = self._session.request(
                method=method, url=url, timeout=self._timeout, **kwargs
            )

            api_message = self._extract_api_message(response)

            if response.status_code == 400:
                message = "Bad Request"
                if api_message:
                    message += f" ({'; '.join(api_message)})"
                raise ValidationError(message, api_message=api_message)
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Unauthorized: Check your access token", api_message=api_message
                )
            elif response.status_code == 403:
                raise ForbiddenError("Forbidden: Insufficient permissions", api_message=api_message)
            elif response.status_code == 404:
                raise ResourceNotFoundError("Not Found", api_message=api_message)
            elif response.status_code == 409:
                raise ConflictError("Conflict", api_message=api_message)
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
                message = "Too Many Requests: Rate limit exceeded"
                if retry_seconds:
                    message += f" - Retry after {retry_seconds} seconds"
                raise RateLimitError(message, api_message=api_message, retry_after=retry_seconds)
            elif response.status_code >= 500:
                raise EnergyTrackerAPIError(
                    f"Server error: {response.status_code}", api_message=api_message
                )
            elif response.status_code >= 400:
                raise EnergyTrackerAPIError(
                    f"HTTP error: {response.status_code}", api_message=api_message
                )

            return response

        except requests.exceptions.Timeout:
            raise EnergyTrackerAPIError(f"Request timeout after {self._timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise EnergyTrackerAPIError(f"Request failed: {str(e)}")

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self) -> "EnergyTrackerClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
