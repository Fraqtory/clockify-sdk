"""
Project model and manager for Clockify API
"""
from typing import Dict, List, Optional

from ..base.client import ClockifyBaseClient


class ProjectManager(ClockifyBaseClient):
    """Manager for Clockify project operations"""

    def __init__(self, api_key: str, workspace_id: str):
        """
        Initialize the project manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_projects(self) -> List[Dict]:
        """
        Get all projects in the workspace

        Returns:
            List of project objects
        """
        return self._request("GET", f"workspaces/{self.workspace_id}/projects")

    def get_project(self, project_id: str) -> Dict:
        """
        Get a specific project by ID

        Args:
            project_id: Project ID

        Returns:
            Project object
        """
        return self._request("GET", f"workspaces/{self.workspace_id}/projects/{project_id}")

    def create_project(self, name: str, client_id: Optional[str] = None) -> Dict:
        """
        Create a new project

        Args:
            name: Project name
            client_id: Optional client ID to associate with the project

        Returns:
            Created project object
        """
        data = {
            "name": name,
            "clientId": client_id
        }
        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/projects",
            data={k: v for k, v in data.items() if v is not None}
        )

    def get_tasks(self, project_id: str) -> List[Dict]:
        """
        Get all tasks for a project

        Args:
            project_id: Project ID to get tasks for

        Returns:
            List of tasks
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("GET", endpoint)

    def create_task(self, project_id: str, name: str, assignee_ids: List[str] = None) -> Dict:
        """
        Create a new task in a project

        Args:
            project_id: Project ID to create task in
            name: Task name
            assignee_ids: Optional list of user IDs to assign to the task

        Returns:
            Task data
        """
        data = {
            "name": name,
            "projectId": project_id
        }

        if assignee_ids:
            data["assigneeIds"] = assignee_ids

        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("POST", endpoint, data=data) 