"""Access token data models for Energy Tracker API."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TokenScope(StrEnum):
    """Access scopes a personal access token can be granted."""

    READ_DAILY_VALUES = "read:daily-values"
    READ_EXTRAPOLATION = "read:extrapolation"
    METER_READING = "meter-reading"
    READ_METER_READING = "read:meter-reading"
    WRITE_METER_READING = "write:meter-reading"
    DELETE_METER_READING = "delete:meter-reading"
    MEASURING_DEVICE = "measuring-device"
    READ_MEASURING_DEVICE = "read:measuring-device"
    WRITE_MEASURING_DEVICE = "write:measuring-device"
    DELETE_MEASURING_DEVICE = "delete:measuring-device"
    ENVIRONMENT_RECORD = "environment-record"
    READ_ENVIRONMENT_RECORD = "read:environment-record"
    WRITE_ENVIRONMENT_RECORD = "write:environment-record"
    DELETE_ENVIRONMENT_RECORD = "delete:environment-record"


def _scope(value: str) -> TokenScope | str:
    try:
        return TokenScope(value)
    except ValueError:
        return value


@dataclass(frozen=True, slots=True)
class TokenStatusDto:
    """Status of the personal access token used by the client.

    Attributes:
        display_name: User-assigned name of the token.
        scopes: Access scopes granted to the token. A scope introduced by a newer
            API is kept as a plain string.
        expires_at: Expiry timestamp, or None if the token does not expire.
    """

    display_name: str
    scopes: list[TokenScope | str]
    expires_at: datetime | None = None

    @classmethod
    def _from_dict(cls, data: dict) -> TokenStatusDto:
        scopes = data["scopes"]
        is_string_list = isinstance(scopes, list) and all(
            isinstance(scope, str) for scope in scopes
        )
        if not is_string_list:
            raise TypeError("scopes must be a list of strings")

        expires_at = None
        if data.get("expiresAt"):
            expires_at = datetime.fromisoformat(data["expiresAt"])

        return cls(
            display_name=data["displayName"],
            scopes=[_scope(scope) for scope in scopes],
            expires_at=expires_at,
        )
