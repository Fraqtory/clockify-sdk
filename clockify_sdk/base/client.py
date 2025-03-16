"""
Base client implementation for Clockify API
"""
from typing import Any, Dict, Optional

import requests


class ClockifyBaseClient:
    """Base client for Clockify API interactions"""
    
    base_url = "https://api.clockify.me/api/v1"
    reports_url = "https://reports.api.clockify.me/v1"

    def __init__(self, api_key: str):
        """
        Initialize the base client

        Args:
            api_key: Clockify API key
        """
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None, 
        is_reports: bool = False
    ) -> Any:
        """
        Make a request to the Clockify API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            is_reports: Whether to use the reports API endpoint

        Returns:
            Response data as dictionary

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        base = self.reports_url if is_reports else self.base_url
        url = f"{base}/{endpoint.lstrip('/')}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )
        response.raise_for_status()

        if response.text:
            return response.json()
        return None 