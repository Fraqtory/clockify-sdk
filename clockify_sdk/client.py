"""
Clockify SDK client implementation
"""
from typing import Any, Dict, List, Optional

from .base.client import ClockifyBaseClient
from .models.client import ClientManager
from .models.project import ProjectManager
from .models.report import ReportManager
from .models.task import TaskManager
from .models.time_entry import TimeEntryManager
from .models.user import UserManager


class ClockifyClient(ClockifyBaseClient):
    """
    Main client for interacting with the Clockify API.
    Provides a standardized interface for all Clockify operations.
    """

    def __init__(self, api_key: str, workspace_id: Optional[str] = None):
        """
        Initialize the Clockify client with your API key

        Args:
            api_key: Your Clockify API key
            workspace_id: Optional workspace ID to use
        """
        super().__init__(api_key)
        
        # Initialize user manager first to get user and workspace info
        self.user_manager = UserManager(api_key)
        
        # Use provided workspace_id or get from user manager
        self.workspace_id = workspace_id or self.user_manager.workspace_id
        self.user_manager.set_active_workspace(self.workspace_id)
        
        # Initialize other managers
        self.time_entries = TimeEntryManager(api_key, self.workspace_id, self.user_manager.user_id)
        self.projects = ProjectManager(api_key, self.workspace_id)
        self.reports = ReportManager(api_key, self.workspace_id)
        self.clients = ClientManager(api_key, self.workspace_id)
        self.tasks = TaskManager(api_key, self.workspace_id)

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
        self.time_entries = TimeEntryManager(self.time_entries.api_key, workspace_id, self.user_manager.user_id)
        self.projects = ProjectManager(self.projects.api_key, workspace_id)
        self.reports = ReportManager(self.reports.api_key, workspace_id)
        self.clients = ClientManager(self.clients.api_key, workspace_id)
        self.tasks = TaskManager(self.tasks.api_key, workspace_id) 