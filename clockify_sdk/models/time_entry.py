"""Time entry management for Clockify API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class TimeEntry(ClockifyBaseModel):
    """Time entry model representing a Clockify time entry."""

    id: str = Field(..., description="Time entry ID")
    description: str = Field(..., description="Time entry description")
    project_id: Optional[str] = Field(None, description="Project ID")
    task_id: Optional[str] = Field(None, description="Task ID")
    user_id: str = Field(..., description="User ID")
    workspace_id: str = Field(..., description="Workspace ID")
    start: datetime = Field(..., description="Start time")
    end: Optional[datetime] = Field(None, description="End time")
    duration: Optional[str] = Field(None, description="Duration in ISO 8601 format")
    billable: bool = Field(False, description="Whether the time entry is billable")
    tags: List[str] = Field(default_factory=list, description="List of tag IDs")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class TimeEntryManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for time entry-related operations."""

    def __init__(
        self, connection_manager: Any, workspace_id: Optional[str] = None
    ) -> None:
        """Initialize the time entry manager.

        Args:
            connection_manager: Connection manager instance
            workspace_id: Optional workspace ID
        """
        super().__init__(connection_manager)
        self.workspace_id = workspace_id

    def get_all(
        self, workspace_id: str, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all time entries in a workspace.

        Args:
            workspace_id: ID of the workspace
            user_id: Optional user ID to filter by

        Returns:
            List of time entries
        """
        params = {"userId": user_id} if user_id else {}
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/time-entries",
            params=params,
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, workspace_id: str, time_entry_id: str) -> Dict[str, Any]:
        """Get a specific time entry by ID.

        Args:
            workspace_id: ID of the workspace
            time_entry_id: ID of the time entry

        Returns:
            Time entry information
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/time-entries/{time_entry_id}",
            response_type=Dict[str, Any],
        )

    def create(self, workspace_id: str, time_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new time entry.

        Args:
            workspace_id: ID of the workspace
            time_entry: Time entry data

        Returns:
            Created time entry information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/time-entries",
            json=time_entry,
            response_type=Dict[str, Any],
        )

    def update(
        self, workspace_id: str, time_entry_id: str, time_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing time entry.

        Args:
            workspace_id: ID of the workspace
            time_entry_id: ID of the time entry
            time_entry: Updated time entry data

        Returns:
            Updated time entry information
        """
        return self._request(
            "PUT",
            f"workspaces/{workspace_id}/time-entries/{time_entry_id}",
            json=time_entry,
            response_type=Dict[str, Any],
        )

    def delete(self, workspace_id: str, time_entry_id: str) -> None:
        """Delete a time entry.

        Args:
            workspace_id: ID of the workspace
            time_entry_id: ID of the time entry
        """
        self._request(
            "DELETE",
            f"workspaces/{workspace_id}/time-entries/{time_entry_id}",
            response_type=Dict[str, Any],
        )

    def start_timer(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a timer.

        Args:
            workspace_id: ID of the workspace
            data: Timer data

        Returns:
            Started timer information
        """
        response = self._request(
            "POST",
            f"workspaces/{workspace_id}/time-entries/timer/start",
            json=data,
            response_type=Dict[str, Any],
        )
        return response

    def stop_timer(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a timer.

        Args:
            workspace_id: ID of the workspace
            data: Timer data

        Returns:
            Stopped timer information
        """
        response = self._request(
            "POST",
            f"workspaces/{workspace_id}/time-entries/timer/stop",
            json=data,
            response_type=Dict[str, Any],
        )
        return response

    def get_current_timer(self, workspace_id: str) -> Dict[str, Any]:
        """Get the current timer.

        Args:
            workspace_id: ID of the workspace

        Returns:
            Current timer information
        """
        response = self._request(
            "GET",
            f"workspaces/{workspace_id}/time-entries/timer",
            response_type=Dict[str, Any],
        )
        return response

    def add_time_entry(
        self,
        start_time: datetime,
        end_time: datetime,
        description: str,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a manual time entry

        Args:
            start_time: Entry start time
            end_time: Entry end time
            description: Time entry description
            project_id: Optional project ID
            task_id: Optional task ID

        Returns:
            Created time entry object
        """
        if not self.workspace_id:
            raise ValueError("workspace_id must be set before calling add_time_entry")

        data: Dict[str, Any] = {
            "start": start_time.isoformat() + "Z",
            "end": end_time.isoformat() + "Z",
            "description": description,
        }
        if project_id:
            data["projectId"] = project_id
        if task_id:
            data["taskId"] = task_id

        response = self._request(
            "POST",
            f"workspaces/{self.workspace_id}/time-entries",
            json=data,
            response_type=Dict[str, Any],
        )
        return response
