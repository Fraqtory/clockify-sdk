"""
Task model and manager for Clockify API
"""
from typing import Dict, List, Optional

from ..base.client import ClockifyBaseClient


class TaskManager(ClockifyBaseClient):
    """Manager for Clockify task operations"""

    def __init__(self, api_key: str, workspace_id: str):
        """
        Initialize the task manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_tasks(self, project_id: str) -> List[Dict]:
        """
        Get all tasks in a project

        Args:
            project_id: Project ID

        Returns:
            List of task objects
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        )

    def get_task(self, project_id: str, task_id: str) -> Dict:
        """
        Get a specific task by ID

        Args:
            project_id: Project ID
            task_id: Task ID

        Returns:
            Task object
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        )

    def create_task(self, project_id: str, name: str) -> Dict:
        """
        Create a new task in a project

        Args:
            project_id: Project ID
            name: Task name

        Returns:
            Created task object
        """
        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks",
            data={"name": name}
        )

    def bulk_create_tasks(self, project_id: str, tasks: List[Dict]) -> List[Dict]:
        """
        Create multiple tasks in a project

        Args:
            project_id: Project ID
            tasks: List of task objects with at least a name field

        Returns:
            List of created task objects
        """
        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/bulk",
            data=tasks
        )

    def update_task(self, project_id: str, task_id: str, name: str) -> Dict:
        """
        Update an existing task

        Args:
            project_id: Project ID
            task_id: Task ID
            name: New task name

        Returns:
            Updated task object
        """
        return self._request(
            "PUT",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}",
            data={"name": name}
        )

    def mark_task_done(self, project_id: str, task_id: str) -> Dict:
        """
        Mark a task as completed

        Args:
            project_id: Project ID
            task_id: Task ID

        Returns:
            Updated task object
        """
        return self._request(
            "PATCH",
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}",
            data={"status": "DONE"}
        )

    def delete_task(self, project_id: str, task_id: str) -> None:
        """
        Delete a task

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to delete
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        self._request("DELETE", endpoint)

    def mark_task_active(self, project_id: str, task_id: str) -> Dict:
        """
        Mark a task as active

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to mark as active

        Returns:
            Updated task data
        """
        return self.update_task(project_id, task_id, status="ACTIVE") 