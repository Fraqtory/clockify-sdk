"""Time entry management for Clockify API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from clockify_sdk.base.client import ClockifyBaseClient


class TimeEntryManager(ClockifyBaseClient):
    """Manager for Clockify time entry operations"""

    def __init__(self, api_key: str, workspace_id: str, user_id: str) -> None:
        """
        Initialize the time entry manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
            user_id: User ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id
        self.user_id = user_id

    def get_time_entries(self) -> List[Dict[str, Any]]:
        """
        Get all time entries for the current user

        Returns:
            List of time entry objects
        """
        endpoint = f"workspaces/{self.workspace_id}/user/{self.user_id}/time-entries"
        return self._request("GET", endpoint)

    def start_timer(
        self,
        description: str,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start a new timer

        Args:
            description: Time entry description
            project_id: Optional project ID
            task_id: Optional task ID

        Returns:
            Created time entry object
        """
        data: Dict[str, Any] = {
            "start": datetime.now().isoformat() + "Z",
            "description": description,
        }
        if project_id:
            data["projectId"] = project_id
        if task_id:
            data["taskId"] = task_id

        endpoint = f"workspaces/{self.workspace_id}/time-entries"
        return self._request("POST", endpoint, data=data)

    def stop_timer(self) -> Dict[str, Any]:
        """
        Stop the current running timer

        Returns:
            Updated time entry object
        """
        data: Dict[str, Any] = {"end": datetime.now().isoformat() + "Z"}
        endpoint = f"workspaces/{self.workspace_id}/user/{self.user_id}/time-entries"
        return self._request("PATCH", endpoint, data=data)

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
        data: Dict[str, Any] = {
            "start": start_time.isoformat() + "Z",
            "end": end_time.isoformat() + "Z",
            "description": description,
        }
        if project_id:
            data["projectId"] = project_id
        if task_id:
            data["taskId"] = task_id

        endpoint = f"workspaces/{self.workspace_id}/time-entries"
        return self._request("POST", endpoint, data=data)
