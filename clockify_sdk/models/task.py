"""
Task model and manager for Clockify API
"""

from typing import Any, Dict, List, Optional

from ..base.client import ClockifyBaseClient


class TaskManager(ClockifyBaseClient):
    """Manager for Clockify task operations"""

    def __init__(self, api_key: str, workspace_id: str) -> None:
        """
        Initialize the task manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks in a project

        Args:
            project_id: Project ID

        Returns:
            List of task objects
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("GET", endpoint)

    def get_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get a specific task by ID

        Args:
            project_id: Project ID
            task_id: Task ID

        Returns:
            Task object
        """
        endpoint = (
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        )
        return self._request("GET", endpoint)

    def create_task(
        self,
        project_id: str,
        name: str,
        assignee_ids: Optional[List[str]] = None,
        estimate: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new task in a project

        Args:
            project_id: Project ID
            name: Task name
            assignee_ids: Optional list of assignee IDs
            estimate: Optional time estimate
            status: Optional task status

        Returns:
            Created task object
        """
        data: Dict[str, Any] = {"name": name}
        if assignee_ids:
            data["assigneeIds"] = assignee_ids
        if estimate:
            data["estimate"] = estimate
        if status:
            data["status"] = status

        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("POST", endpoint, data=data)

    def bulk_create_tasks(
        self,
        project_id: str,
        tasks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Create multiple tasks in a project

        Args:
            project_id: Project ID
            tasks: List of task objects with at least a name field

        Returns:
            List of created task objects
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/bulk"
        return self._request("POST", endpoint, data={"tasks": tasks})

    def update_task(
        self,
        project_id: str,
        task_id: str,
        name: Optional[str] = None,
        assignee_ids: Optional[List[str]] = None,
        estimate: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing task

        Args:
            project_id: Project ID
            task_id: Task ID
            name: New task name
            assignee_ids: Optional list of assignee IDs
            estimate: Optional time estimate
            status: Optional task status

        Returns:
            Updated task object
        """
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if assignee_ids:
            data["assigneeIds"] = assignee_ids
        if estimate:
            data["estimate"] = estimate
        if status:
            data["status"] = status

        endpoint = (
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        )
        return self._request("PUT", endpoint, data=data)

    def mark_task_done(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as completed

        Args:
            project_id: Project ID
            task_id: Task ID

        Returns:
            Updated task object
        """
        return self.update_task(project_id, task_id, status="DONE")

    def delete_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """
        Delete a task

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to delete

        Returns:
            Deleted task
        """
        endpoint = (
            f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        )
        return self._request("DELETE", endpoint)

    def mark_task_active(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as active

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to mark as active

        Returns:
            Updated task data
        """
        return self.update_task(project_id, task_id, status="ACTIVE")
