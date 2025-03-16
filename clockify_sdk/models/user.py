"""User management for Clockify API."""

from typing import Optional

from clockify_sdk.base.client import ClockifyBaseClient, JsonDict, JsonList


class UserManager(ClockifyBaseClient):
    """Manager for Clockify user operations"""

    def __init__(self, api_key: str) -> None:
        """
        Initialize the user manager

        Args:
            api_key: Clockify API key
        """
        super().__init__(api_key)
        self.user_id: Optional[str] = None
        self.workspace_id: Optional[str] = None
        self._initialize_user()

    def _initialize_user(self) -> None:
        """Initialize user and workspace IDs"""
        user = self.get_current_user()
        self.user_id = user["id"]
        workspaces = self.get_workspaces()
        self.workspace_id = workspaces[0]["id"] if workspaces else None

    def get_current_user(self) -> JsonDict:
        """
        Get the current user's information

        Returns:
            User object
        """
        response = self._request("GET", "user", response_type=JsonDict)
        self.user_id = response["id"]
        return response

    def get_workspaces(self) -> JsonList:
        """
        Get all workspaces for the current user

        Returns:
            List of workspace objects
        """
        return self._request("GET", "workspaces", response_type=JsonList)

    def set_active_workspace(self, workspace_id: str) -> None:
        """
        Set the active workspace

        Args:
            workspace_id: Workspace ID
        """
        self.workspace_id = workspace_id
