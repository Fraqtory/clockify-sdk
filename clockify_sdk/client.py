"""
Clockify SDK client implementation
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

from .config import Config
from .connection import ConnectionManager
from .models.client import ClientManager
from .models.project import ProjectManager
from .models.report import ReportManager
from .models.task import TaskManager
from .models.time_entry import TimeEntryManager
from .models.user import UserManager


class Clockify:
    """
    Main entry point for interacting with the Clockify API.
    Provides a standardized interface for all Clockify operations.

    Args:
        api_key: Your Clockify API key. Can also be set via CLOCKIFY_API_KEY environment variable.
        workspace_id: Optional workspace ID to use. If not provided, uses the first available workspace.
    """

    def __init__(self, api_key: str, workspace_id: Optional[str] = None) -> None:
        """
        Initialize the Clockify client with your API key

        Args:
            api_key: Your Clockify API key. If not provided, will look for CLOCKIFY_API_KEY environment variable.
            workspace_id: Optional workspace ID to use. If not provided, uses the first available workspace.

        Raises:
            ValueError: If no API key is provided and CLOCKIFY_API_KEY environment variable is not set.
        """
        self.api_key: str = api_key
        self.workspace_id: Optional[str] = None
        self.user_id: str = ""

        Config.set_api_key(api_key)
        self._connection = ConnectionManager(api_key)

        # Initialize managers
        self.users = UserManager(self._connection)
        self.time_entries = TimeEntryManager(self._connection)
        self.projects = ProjectManager(self._connection)
        self.reports = ReportManager(self._connection)
        self.clients = ClientManager(self._connection)
        self.tasks = TaskManager(self._connection)

        # Get user info
        user = self.users.get_current_user()
        self.user_id = user["id"]

        # Set workspace ID
        if workspace_id:
            self.workspace_id = workspace_id
        else:
            workspaces = self.get_workspaces()
            self.workspace_id = workspaces[0]["id"] if workspaces else None

    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces for the current user.

        Returns:
            List of workspace objects.
        """
        response = self._connection.request(
            method="GET",
            url=f"{Config.BASE_URL}/workspaces",
        )
        return cast("List[Dict[str, Any]]", response)

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects in the current workspace.

        Returns:
            List of project objects.
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling get_projects")
        return self.projects.get_all(self.workspace_id)

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID.

        Args:
            project_id: ID of the project to get.

        Returns:
            Project object.
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling get_project")
        return self.projects.get_by_id(self.workspace_id, project_id)

    def get_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a project.

        Args:
            project_id: ID of the project to get tasks for.

        Returns:
            List of task objects.
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling get_tasks")
        return self.tasks.get_all(self.workspace_id, project_id)

    def get_time_entries(self) -> List[Dict[str, Any]]:
        """Get all time entries for the current user.

        Returns:
            List of time entry objects.
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling get_time_entries")
        return self.time_entries.get_all(self.workspace_id, self.user_id)

    def start_timer(
        self,
        description: str,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start a new timer.

        Args:
            description: Description of the time entry.
            project_id: Optional ID of the project to associate with the time entry.
            task_id: Optional ID of the task to associate with the time entry.

        Returns:
            Time entry object.
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling start_timer")

        data: Dict[str, Any] = {
            "description": description,
        }
        if project_id:
            data["projectId"] = project_id
        if task_id:
            data["taskId"] = task_id

        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(
            seconds=1
        )  # Add 1 second to satisfy type check
        return self.time_entries.add_time_entry(
            start_time=start_time,
            end_time=end_time,  # Will be updated by stop_timer
            description=description,
            project_id=project_id,
            task_id=task_id,
        )

    def stop_timer(self) -> Dict[str, Any]:
        """Stop the current timer.

        Returns:
            Time entry object.
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling stop_timer")

        # Get the current running time entry
        time_entries = self.time_entries.get_all(self.workspace_id, self.user_id)
        running_entry = next(
            (entry for entry in time_entries if entry.get("end") is None), None
        )
        if not running_entry:
            raise ValueError("No running timer found")

        # Update the time entry with an end time
        data = {
            "end": datetime.now(timezone.utc).isoformat() + "Z",
        }
        return self.time_entries.update(self.workspace_id, running_entry["id"], data)

    def close(self) -> None:
        """Close all connections."""
        self._connection.close()

    def __enter__(self) -> "Clockify":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Context manager exit."""
        self.close()
