"""
Task model for the Clockify SDK
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class Task(ClockifyBaseModel):
    """Task model representing a Clockify task."""

    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    project_id: str = Field(..., description="Project ID")
    workspace_id: str = Field(..., description="Workspace ID")
    user_group_id: Optional[str] = Field(None, description="User group ID")
    assignee_id: Optional[str] = Field(None, description="Assignee ID")
    estimate: Optional[str] = Field(
        None, description="Estimated duration in ISO 8601 format"
    )
    status: str = Field(..., description="Task status")
    is_active: bool = Field(True, description="Whether the task is active")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class TaskManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for task-related operations."""

    def get_all(self, workspace_id: str, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks in a project.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project

        Returns:
            List of tasks
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/projects/{project_id}/tasks",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(
        self, workspace_id: str, project_id: str, task_id: str
    ) -> Dict[str, Any]:
        """Get a specific task by ID.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Task information
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
            response_type=Dict[str, Any],
        )

    def create(
        self, workspace_id: str, project_id: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new task.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            task: Task data

        Returns:
            Created task information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/projects/{project_id}/tasks",
            json=task,
            response_type=Dict[str, Any],
        )

    def update(
        self, workspace_id: str, project_id: str, task_id: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing task.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            task_id: ID of the task
            task: Updated task data

        Returns:
            Updated task information
        """
        return self._request(
            "PUT",
            f"workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
            json=task,
            response_type=Dict[str, Any],
        )

    def delete(self, workspace_id: str, project_id: str, task_id: str) -> None:
        """Delete a task.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            task_id: ID of the task
        """
        self._request(
            "DELETE",
            f"workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
            response_type=Dict[str, Any],
        )

    def bulk_create(
        self, workspace_id: str, project_id: str, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create multiple tasks at once.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            tasks: List of task data

        Returns:
            List of created task information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/projects/{project_id}/tasks/bulk",
            json={"tasks": tasks},
            response_type=List[Dict[str, Any]],
        )

    def mark_task_done(
        self, workspace_id: str, project_id: str, task_id: str
    ) -> Dict[str, Any]:
        """Mark a task as done.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Updated task information
        """
        return self.update(workspace_id, project_id, task_id, {"status": "DONE"})

    def mark_task_active(
        self, workspace_id: str, project_id: str, task_id: str
    ) -> Dict[str, Any]:
        """Mark a task as active.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            task_id: ID of the task

        Returns:
            Updated task information
        """
        return self.update(workspace_id, project_id, task_id, {"status": "ACTIVE"})
