"""
Time entry model and manager for Clockify API
"""
from datetime import datetime
from typing import Dict, List, Optional

from ..base.client import ClockifyBaseClient
from ..utils.date_utils import format_datetime


class TimeEntryManager(ClockifyBaseClient):
    """Manager for Clockify time entry operations"""

    def __init__(self, api_key: str, workspace_id: str, user_id: str):
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

    def get_time_entries(self) -> List[Dict]:
        """
        Get all time entries for the current user

        Returns:
            List of time entry objects
        """
        return self._request(
            "GET",
            f"workspaces/{self.workspace_id}/user/{self.user_id}/time-entries"
        )

    def start_timer(
        self,
        description: str,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict:
        """
        Start a new timer

        Args:
            description: Time entry description
            project_id: Optional project ID
            task_id: Optional task ID

        Returns:
            Created time entry object
        """
        data = {
            "start": format_datetime(datetime.now()),
            "description": description,
            "projectId": project_id,
            "taskId": task_id
        }
        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/time-entries",
            data={k: v for k, v in data.items() if v is not None}
        )

    def stop_timer(self) -> Dict:
        """
        Stop the current running timer

        Returns:
            Updated time entry object
        """
        return self._request(
            "PATCH",
            f"workspaces/{self.workspace_id}/user/{self.user_id}/time-entries",
            data={"end": format_datetime(datetime.now())}
        )

    def add_time_entry(
        self,
        start_time: datetime,
        end_time: datetime,
        description: str,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict:
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
        data = {
            "start": format_datetime(start_time),
            "end": format_datetime(end_time),
            "description": description,
            "projectId": project_id,
            "taskId": task_id
        }
        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/time-entries",
            data={k: v for k, v in data.items() if v is not None}
        ) 