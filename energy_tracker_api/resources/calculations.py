"""Server-side daily values and extrapolations for standard devices."""

from datetime import UTC, datetime
from http import HTTPStatus

from ..exceptions import ValidationError
from ..models import CalculationInterval, CalculationPointDto, ExtrapolationMethod
from .base import BaseResource


def _query_params(
    from_timestamp: datetime | None,
    to_timestamp: datetime | None,
    time_zone: str | None,
) -> dict[str, str]:
    params: dict[str, str] = {}
    for key, timestamp in (("from", from_timestamp), ("to", to_timestamp)):
        if timestamp is None:
            continue
        if not isinstance(timestamp, datetime) or timestamp.utcoffset() is None:
            raise ValidationError(f"{key} must be a datetime with a UTC offset")
        try:
            params[key] = timestamp.astimezone(UTC).isoformat()
        except (ValueError, OverflowError) as error:
            raise ValidationError(f"{key} cannot be represented as a UTC timestamp") from error
    if time_zone is not None:
        params["timeZone"] = time_zone
    return params


class CalculationResource(BaseResource):
    """Handler for calculations; values and calendar boundaries are computed by the API."""

    async def daily_values(
        self,
        device_id: str,
        *,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        time_zone: str | None = None,
    ) -> list[CalculationPointDto]:
        """Return reading-backed daily points. Requires scope ``read:daily-values``.

        Args:
            device_id: Standard device identifier.
            from_timestamp: Inclusive start, with a UTC offset. Omit for no lower filter.
            to_timestamp: Exclusive end, with a UTC offset. Omit for no upper filter.
            time_zone: IANA time zone; defaults to the device location zone, then UTC.

        The server rounds the start down and end up to day boundaries in time_zone.
        An explicit end cannot extend beyond tomorrow. Insufficient readings return [].
        Points remain in server order, including terminal points with zero duration.

        Raises:
            ValidationError: Invalid input or exceeded calculation limits.
            AuthenticationError: Invalid access token.
            ForbiddenError: Missing scope or blocked access.
            ResourceNotFoundError: Device does not exist or is not owned by the user.
            ConflictError: Ambiguous or unrepresentable meter history.
            RateLimitError: Request limit exceeded.
            ServiceUnavailableError: Calculation unavailable or server deadline exceeded.
            TimeoutError: Client calculation timeout exceeded.
            EnergyTrackerAPIError: Invalid response or another API/transport failure.
        """
        params = _query_params(from_timestamp, to_timestamp, time_zone)
        return await self._request_model_list(
            response_type=CalculationPointDto,
            method="GET",
            endpoint=f"/v1/devices/standard/{device_id}/daily-values",
            expected_status=HTTPStatus.OK,
            params=params or None,
            timeout=self._client._calculation_timeout,
        )

    async def extrapolations(
        self,
        device_id: str,
        *,
        interval: CalculationInterval,
        method: ExtrapolationMethod = ExtrapolationMethod.STANDARD,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        time_zone: str | None = None,
    ) -> list[CalculationPointDto]:
        """Return estimates for calendar intervals. Requires scope ``read:extrapolation``.

        Args:
            device_id: Standard device identifier.
            interval: Day, week, month, quarter or year. Weeks begin on Monday.
            method: Calculation method; currently only standard is supported.
            from_timestamp: Inclusive start with a UTC offset; defaults to current interval start.
            to_timestamp: Exclusive end with a UTC offset; defaults to next interval start.
            time_zone: IANA time zone; defaults to the device location zone, then UTC.

        The server rounds the start down and end up to interval boundaries. Output
        is limited to 366 calendar days and input to 2,000 readings including boundary
        readings. The horizon includes the interval containing twelve months after the
        latest reading. Insufficient readings return []. expected_value is the entire
        estimate for an interval: do not add actual_value. Errors match daily_values().
        """
        try:
            interval = CalculationInterval(interval)
            method = ExtrapolationMethod(method)
        except (ValueError, TypeError) as error:
            raise ValidationError(
                "Unsupported calculation interval or extrapolation method"
            ) from error
        params = _query_params(from_timestamp, to_timestamp, time_zone)
        return await self._request_model_list(
            response_type=CalculationPointDto,
            method="GET",
            endpoint=f"/v1/devices/standard/{device_id}/extrapolations/{method.value}/{interval.value}",
            expected_status=HTTPStatus.OK,
            params=params or None,
            timeout=self._client._calculation_timeout,
        )
