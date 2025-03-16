"""
Base client implementation for Clockify API
"""

from typing import Any, Dict, List, Optional, TypeVar, Union, cast

import requests

# Define response types
JsonDict = Dict[str, Any]
JsonList = List[JsonDict]
JsonResponse = Union[JsonDict, JsonList]

# Type variable for generic response types
T = TypeVar("T")


class ClockifyBaseClient:
    """Base client for Clockify API."""

    def __init__(self, api_key: str) -> None:
        """
        Initialize the base client

        Args:
            api_key: Clockify API key
        """
        self.api_key = api_key
        self.base_url = "https://api.clockify.me/api/v1"
        self.reports_url = "https://reports.api.clockify.me/v1"
        self.headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        is_reports: bool = False,
        response_type: type[T] = JsonResponse,  # type: ignore
    ) -> T:
        """
        Make a request to the Clockify API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            is_reports: Whether to use the reports API endpoint
            response_type: Expected response type

        Returns:
            Response data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        base = self.reports_url if is_reports else self.base_url
        url = f"{base}/{endpoint.lstrip('/')}"

        response = requests.request(
            method=method, url=url, headers=self.headers, params=params, json=data
        )
        response.raise_for_status()

        return cast(T, response.json())
