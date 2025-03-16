from typing import Dict, List, Optional
from ..base.client import ClockifyClient

class TaskManager(ClockifyClient):
    """Handles task operations in Clockify"""

    def __init__(self, api_key: str, workspace_id: str):
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_tasks(self, project_id: str, page_size: int = 50) -> List[Dict]:
        """
        Get all tasks for a project

        Args:
            project_id: ID of the project to get tasks from
            page_size: Number of tasks to return per page

        Returns:
            List of tasks
        """
        params = {"page-size": page_size}
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("GET", endpoint, params=params)

    def get_task(self, project_id: str, task_id: str) -> Dict:
        """
        Get a specific task by ID

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to retrieve

        Returns:
            Task data
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        return self._request("GET", endpoint)

    def create_task(self, project_id: str, name: str, assignee_ids: List[str] = None,
                    estimate: str = None, status: str = "ACTIVE") -> Dict:
        """
        Create a new task in a project

        Args:
            project_id: ID of the project to create task in
            name: Name of the task
            assignee_ids: Optional list of user IDs to assign to the task
            estimate: Optional time estimate in format 'PT#H#M' (e.g., 'PT2H30M' for 2.5 hours)
            status: Task status (ACTIVE or DONE)

        Returns:
            Created task data
        """
        data = {
            "name": name,
            "projectId": project_id,
            "status": status
        }

        if assignee_ids:
            data["assigneeIds"] = assignee_ids
        if estimate:
            data["estimate"] = estimate

        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("POST", endpoint, data=data)

    def update_task(self, project_id: str, task_id: str, name: Optional[str] = None,
                    assignee_ids: Optional[List[str]] = None, estimate: Optional[str] = None,
                    status: Optional[str] = None) -> Dict:
        """
        Update an existing task

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to update
            name: Optional new name for the task
            assignee_ids: Optional list of user IDs to assign to the task
            estimate: Optional time estimate in format 'PT#H#M'
            status: Optional task status (ACTIVE or DONE)

        Returns:
            Updated task data
        """
        data = {}
        if name:
            data["name"] = name
        if assignee_ids is not None:  # Allow empty list to remove all assignees
            data["assigneeIds"] = assignee_ids
        if estimate:
            data["estimate"] = estimate
        if status:
            data["status"] = status

        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        return self._request("PUT", endpoint, data=data)

    def delete_task(self, project_id: str, task_id: str) -> None:
        """
        Delete a task

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to delete
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/{task_id}"
        self._request("DELETE", endpoint)

    def bulk_create_tasks(self, project_id: str, tasks: List[Dict]) -> List[Dict]:
        """
        Create multiple tasks in a project at once

        Args:
            project_id: ID of the project to create tasks in
            tasks: List of task data dictionaries, each containing:
                  - name: Task name
                  - assigneeIds: Optional list of user IDs
                  - estimate: Optional time estimate
                  - status: Optional status (ACTIVE or DONE)

        Returns:
            List of created tasks
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks/bulk"
        return self._request("POST", endpoint, data=tasks)

    def mark_task_done(self, project_id: str, task_id: str) -> Dict:
        """
        Mark a task as completed

        Args:
            project_id: ID of the project containing the task
            task_id: ID of the task to mark as done

        Returns:
            Updated task data
        """
        return self.update_task(project_id, task_id, status="DONE")

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