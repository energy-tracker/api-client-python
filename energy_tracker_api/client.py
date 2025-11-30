"""Energy Tracker API client implementation."""

import asyncio
from typing import Any, Optional
from urllib.parse import urljoin

import aiohttp

from .exceptions import (
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


class EnergyTrackerClient:
    """Async client for interacting with the Energy Tracker public REST API."""

    _DEFAULT_BASE_URL = "https://public-api.energy-tracker.best-ios-apps.de"

    _base_url: str
    _access_token: str
    _timeout: aiohttp.ClientTimeout
    _session: Optional[aiohttp.ClientSession]

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
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = None

        from .resources import MeterReadingResource

        self.meter_readings = MeterReadingResource(self)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=self._timeout,
            )
            self._session = session
            return session
        return self._session

    def _extract_api_message(self, data: dict[str, Any]) -> list[str]:
        message = data.get("message")

        if isinstance(message, list):
            return [str(m) for m in message]
        elif isinstance(message, str):
            return [message]
        else:
            return []

    async def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> aiohttp.ClientResponse:
        session = await self._get_session()
        url = urljoin(self._base_url, endpoint)

        try:
            async with session.request(method=method, url=url, **kwargs) as response:
                try:
                    data = await response.json()
                except (aiohttp.ContentTypeError, ValueError):
                    data = {}

                api_message = self._extract_api_message(data)

                if response.status == 400:
                    message = "Bad Request"
                    if api_message:
                        message += f" ({'; '.join(api_message)})"
                    raise ValidationError(message, api_message=api_message)
                elif response.status == 401:
                    raise AuthenticationError(
                        "Unauthorized: Check your access token", api_message=api_message
                    )
                elif response.status == 403:
                    raise ForbiddenError(
                        "Forbidden: Insufficient permissions", api_message=api_message
                    )
                elif response.status == 404:
                    raise ResourceNotFoundError("Not Found", api_message=api_message)
                elif response.status == 409:
                    raise ConflictError("Conflict", api_message=api_message)
                elif response.status == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_seconds = (
                        int(retry_after) if retry_after and retry_after.isdigit() else None
                    )
                    message = "Too Many Requests: Rate limit exceeded"
                    if retry_seconds:
                        message += f" - Retry after {retry_seconds} seconds"
                    raise RateLimitError(
                        message, api_message=api_message, retry_after=retry_seconds
                    )
                elif response.status >= 500:
                    raise EnergyTrackerAPIError(
                        f"Server error: {response.status}", api_message=api_message
                    )
                elif response.status >= 400:
                    raise EnergyTrackerAPIError(
                        f"HTTP error: {response.status}", api_message=api_message
                    )

                return response

        except aiohttp.ClientError as e:
            raise NetworkError(f"Request failed: {str(e)}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timeout after {self._timeout.total} seconds")

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "EnergyTrackerClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
