"""
User model and manager for Clockify API
"""
from typing import Dict, List

from ..base.client import ClockifyBaseClient


class UserManager(ClockifyBaseClient):
    """Manager for Clockify user operations"""

    def __init__(self, api_key: str):
        """
        Initialize the user manager

        Args:
            api_key: Clockify API key
        """
        super().__init__(api_key)
        self.user_id = None
        self.workspace_id = None
        self._initialize_user()

    def _initialize_user(self) -> None:
        """Initialize user and workspace IDs"""
        user = self.get_current_user()
        self.user_id = user["id"]
        workspaces = self.get_workspaces()
        self.workspace_id = workspaces[0]["id"] if workspaces else None

    def get_current_user(self) -> Dict:
        """
        Get the current user's information

        Returns:
            User object
        """
        return self._request("GET", "user")

    def get_workspaces(self) -> List[Dict]:
        """
        Get all workspaces for the current user

        Returns:
            List of workspace objects
        """
        return self._request("GET", "workspaces")

    def set_active_workspace(self, workspace_id: str) -> None:
        """
        Set the active workspace

        Args:
            workspace_id: Workspace ID
        """
        self.workspace_id = workspace_id 