"""
Clockify SDK client implementation
"""

from typing import Any, Dict, List, Optional

from clockify_sdk.base.client import ClockifyBaseClient
from clockify_sdk.models.client import ClientManager
from clockify_sdk.models.project import ProjectManager
from clockify_sdk.models.report import ReportManager
from clockify_sdk.models.task import TaskManager
from clockify_sdk.models.time_entry import TimeEntryManager
from clockify_sdk.models.user import UserManager


class ClockifyClient(ClockifyBaseClient):
    """
    Main client for interacting with the Clockify API.
    Provides a standardized interface for all Clockify operations.
    """

    def __init__(self, api_key: str, workspace_id: Optional[str] = None) -> None:
        """
        Initialize the Clockify client with your API key

        Args:
            api_key: Your Clockify API key
            workspace_id: Optional workspace ID to use
        """
        super().__init__(api_key)

        # Initialize user manager first to get user and workspace info
        self.user_manager = UserManager(self.api_key)
        self.user_id = self.user_manager.get_current_user()["id"]

        # Use provided workspace_id or get from user manager
        self.workspace_id = workspace_id or self.user_manager.get_workspaces()[0]["id"]
        self.user_manager.set_active_workspace(self.workspace_id)

        # Initialize other managers
        self.time_entries = TimeEntryManager(
            self.api_key, self.workspace_id, self.user_id
        )
        self.projects = ProjectManager(self.api_key, self.workspace_id)
        self.reports = ReportManager(self.api_key, self.workspace_id)
        self.clients = ClientManager(self.api_key, self.workspace_id)
        self.tasks = TaskManager(self.api_key, self.workspace_id)

    def get_workspaces(self) -> List[Dict[str, Any]]:
        """
        Get all workspaces for the authenticated user

        Returns:
            List of workspace objects
        """
        return self._request("GET", "workspaces")

    def set_active_workspace(self, workspace_id: str) -> None:
        """
        Set the active workspace for all managers

        Args:
            workspace_id: The workspace ID to set as active
        """
        self.workspace_id = workspace_id
        self.user_manager.set_active_workspace(workspace_id)

        # Reinitialize managers with new workspace
        self.time_entries = TimeEntryManager(self.api_key, workspace_id, self.user_id)
        self.projects = ProjectManager(self.api_key, workspace_id)
        self.reports = ReportManager(self.api_key, workspace_id)
        self.clients = ClientManager(self.api_key, workspace_id)
        self.tasks = TaskManager(self.api_key, workspace_id)
