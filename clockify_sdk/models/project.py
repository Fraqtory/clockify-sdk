"""
Project model for the Clockify SDK
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class Project(ClockifyBaseModel):
    """Project model representing a Clockify project."""

    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    workspace_id: str = Field(..., description="Workspace ID")
    client_id: Optional[str] = Field(None, description="Client ID")
    is_private: bool = Field(False, description="Whether the project is private")
    is_archived: bool = Field(False, description="Whether the project is archived")
    duration: Optional[str] = Field(
        None, description="Project duration in ISO 8601 format"
    )
    color: Optional[str] = Field(None, description="Project color")
    billable: bool = Field(False, description="Whether the project is billable")
    template: bool = Field(False, description="Whether the project is a template")
    note: Optional[str] = Field(None, description="Project note")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class ProjectManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for project-related operations."""

    def get_all(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all projects in a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of projects
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/projects",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, workspace_id: str, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project

        Returns:
            Project information
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/projects/{project_id}",
            response_type=Dict[str, Any],
        )

    def create(self, workspace_id: str, project: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project.

        Args:
            workspace_id: ID of the workspace
            project: Project data

        Returns:
            Created project information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/projects",
            json=project,
            response_type=Dict[str, Any],
        )

    def update(
        self, workspace_id: str, project_id: str, project: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing project.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            project: Updated project data

        Returns:
            Updated project information
        """
        return self._request(
            "PUT",
            f"workspaces/{workspace_id}/projects/{project_id}",
            json=project,
            response_type=Dict[str, Any],
        )

    def delete(self, workspace_id: str, project_id: str) -> None:
        """Delete a project.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
        """
        self._request(
            "DELETE",
            f"workspaces/{workspace_id}/projects/{project_id}",
            response_type=Dict[str, Any],
        )

    def get_tasks(self, workspace_id: str, project_id: str) -> List[Dict[str, Any]]:
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

    def get_users(self, workspace_id: str, project_id: str) -> List[Dict[str, Any]]:
        """Get all users in a project.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project

        Returns:
            List of users
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/projects/{project_id}/users",
            response_type=List[Dict[str, Any]],
        )

    def add_user(
        self, workspace_id: str, project_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Add a user to a project.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            user_id: ID of the user

        Returns:
            Updated project information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/projects/{project_id}/users",
            json={"userId": user_id},
            response_type=Dict[str, Any],
        )

    def remove_user(self, workspace_id: str, project_id: str, user_id: str) -> None:
        """Remove a user from a project.

        Args:
            workspace_id: ID of the workspace
            project_id: ID of the project
            user_id: ID of the user
        """
        self._request(
            "DELETE",
            f"workspaces/{workspace_id}/projects/{project_id}/users/{user_id}",
            response_type=Dict[str, Any],
        )
