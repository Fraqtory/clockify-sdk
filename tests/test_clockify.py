"""
Tests for the Clockify SDK
"""
import os
from unittest import TestCase, mock

from clockify_sdk import ClockifyClient


class TestClockifyClient(TestCase):
    """Test cases for ClockifyClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        self.client = ClockifyClient(api_key=self.api_key)

    def test_init(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_key, self.api_key)

    @mock.patch("clockify_sdk.client.requests.get")
    def test_get_workspaces(self, mock_get):
        """Test getting workspaces"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.json.return_value = [
            {"id": "123", "name": "Test Workspace"}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Make request
        workspaces = self.client.get_workspaces()

        # Verify response
        self.assertEqual(len(workspaces), 1)
        self.assertEqual(workspaces[0]["id"], "123")
        self.assertEqual(workspaces[0]["name"], "Test Workspace")

        # Verify request
        mock_get.assert_called_once_with(
            "https://api.clockify.me/api/v1/workspaces",
            headers={"X-Api-Key": self.api_key}
        ) 