from typing import Dict, List, Optional
from ..base.client import ClockifyClient

class ProjectManager(ClockifyClient):
    """Handles project operations in Clockify"""

    def __init__(self, api_key: str, workspace_id: str):
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_projects(self) -> List[Dict]:
        """Get all projects in the active workspace"""
        endpoint = f"workspaces/{self.workspace_id}/projects"
        return self._request("GET", endpoint)

    def create_project(self, name: str, client_id: Optional[str] = None,
                       is_public: bool = True, billable: bool = False,
                       color: str = "#03A9F4") -> Dict:
        """
        Create a new project

        Args:
            name: Project name
            client_id: Optional client ID to associate with project
            is_public: Whether the project is public to workspace members
            billable: Whether the project is billable
            color: Project color code

        Returns:
            Project data
        """
        data = {
            "name": name,
            "isPublic": is_public,
            "billable": billable,
            "color": color
        }

        if client_id:
            data["clientId"] = client_id

        endpoint = f"workspaces/{self.workspace_id}/projects"
        return self._request("POST", endpoint, data=data)

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