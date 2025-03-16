import requests
from typing import Dict, Any

class ClockifyClient:
    """Base client for Clockify API interactions"""
    
    BASE_URL = "https://api.clockify.me/api/v1"
    REPORTS_URL = "https://reports.api.clockify.me/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None, is_reports: bool = False) -> Any:
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
        """
        base = self.REPORTS_URL if is_reports else self.BASE_URL
        url = f"{base}/{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )

        if response.status_code >= 400:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        if response.text:
            return response.json()
        return None 