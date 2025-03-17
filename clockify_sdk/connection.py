"""
Connection manager for the Clockify SDK
"""

from typing import Any, Dict, Optional

import httpx

from clockify_sdk.config import Config
from clockify_sdk.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
)


class ConnectionManager:
    """Connection manager for making HTTP requests to the Clockify API."""

    def __init__(self, api_key: str):
        """Initialize the connection manager.

        Args:
            api_key: Clockify API key
        """
        self.api_key = api_key
        self.timeout = Config.get_timeout()
        self.max_retries = 3
        self.pool_connections = 10
        self.pool_maxsize = 10

        # Create client with connection pooling and retry strategy
        self.client = httpx.Client(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=self.pool_connections,
                max_keepalive_connections=self.pool_maxsize,
            ),
            transport=httpx.HTTPTransport(retries=self.max_retries),
        )

    def request(
        self,
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a request to the Clockify API.

        Args:
            method: HTTP method
            url: URL to request
            json: Optional JSON data
            params: Optional query parameters
            headers: Optional headers

        Returns:
            Response data as JSON

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            ResourceNotFoundError: If resource is not found
            APIError: If any other error occurs
        """
        if not headers:
            headers = {}
        headers["X-Api-Key"] = self.api_key

        try:
            response = self.client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key") from e
            if e.response.status_code == 403:
                raise AuthenticationError("Insufficient permissions") from e
            if e.response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {url}") from e
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After", "60")
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds"
                ) from e
            raise APIError(f"API request failed: {e!s}") from e
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {e!s}") from e

    def close(self) -> None:
        """Close the connection manager."""
        self.client.close()
