"""Base resource with generic deserialization helpers.

Provides the Python equivalent of Swift's Codable/Decodable pattern
using Protocol (PEP 544) and TypeVar for type-safe API response parsing.
"""

from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeVar, cast

from ..exceptions import EnergyTrackerAPIError

if TYPE_CHECKING:
    from ..client import EnergyTrackerClient


class _Deserializable(Protocol):
    """Protocol for API response models that can be deserialized from dicts.

    Any dataclass with a ``_from_dict(cls, data: dict)`` classmethod
    automatically satisfies this protocol through structural subtyping
    (PEP 544) — no explicit inheritance required.
    """

    @classmethod
    def _from_dict(cls, data: dict) -> _Deserializable: ...


_ModelT = TypeVar("_ModelT", bound=_Deserializable)


class BaseResource:
    """Base class for API resource handlers.

    Provides typed helper methods for deserializing API responses
    into model instances, analogous to Swift's generic decoding:

    .. code-block:: swift

        func request<T: Decodable>(_ type: T.Type, ...) async throws -> T

    Subclasses call ``_request_model`` or ``_request_model_list`` instead
    of manually calling ``_make_request`` + ``_from_dict``.
    """

    def __init__(self, client: EnergyTrackerClient) -> None:
        self._client = client

    _HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

    async def _request_model(
        self,
        response_type: type[_ModelT],
        method: _HttpMethod,
        endpoint: str,
        **kwargs: Any,
    ) -> _ModelT:
        """Make an API request and deserialize the response into a model.

        Args:
            response_type: The model class to deserialize into.
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            **kwargs: Additional arguments forwarded to aiohttp.

        Returns:
            A single deserialized model instance.
        """
        data = await self._client._make_request(method=method, endpoint=endpoint, **kwargs)
        if not isinstance(data, dict):
            raise EnergyTrackerAPIError(f"Expected dict response, got {type(data).__name__}")
        return cast(_ModelT, response_type._from_dict(data))

    async def _request_model_list(
        self,
        response_type: type[_ModelT],
        method: _HttpMethod,
        endpoint: str,
        **kwargs: Any,
    ) -> list[_ModelT]:
        """Make an API request and deserialize the response into a list of models.

        Args:
            response_type: The model class to deserialize each item into.
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            **kwargs: Additional arguments forwarded to aiohttp.

        Returns:
            A list of deserialized model instances.
        """
        data = await self._client._make_request(method=method, endpoint=endpoint, **kwargs)
        if not isinstance(data, list):
            raise EnergyTrackerAPIError(f"Expected list response, got {type(data).__name__}")
        return [cast(_ModelT, response_type._from_dict(item)) for item in data]
