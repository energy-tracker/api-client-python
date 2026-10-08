"""Access token resource handler for Energy Tracker API."""

from ..models import TokenStatusDto
from .base import BaseResource


class TokenResource(BaseResource):
    """Handler for the personal access token used by the client."""

    async def status(self) -> TokenStatusDto:
        """Returns the name, scopes and expiry of the access token in use.

        Requires no scope, so it also works for write-only tokens, and does not
        create or change data. The API limits this endpoint to 5 requests per
        5 minutes, including attempts with a missing or invalid token. Call it
        when configuring an integration or checking credentials; do not poll it.

        Returns:
            Status of the access token.

        Raises:
            AuthenticationError: If the token is missing, invalid, expired or revoked.
            ForbiddenError: If the account is suspended.
            RateLimitError: If rate limit is exceeded.
            EnergyTrackerAPIError: For other API errors.
        """
        return await self._request_model(
            response_type=TokenStatusDto,
            method="GET",
            endpoint="/v1/token/status",
        )
