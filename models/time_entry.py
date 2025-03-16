from typing import Dict, List, Optional
from datetime import datetime
from ..base.client import ClockifyClient
from ..utils.date_utils import format_date, get_current_utc_time

class TimeEntryManager(ClockifyClient):
    """Handles time entry operations in Clockify"""

    def __init__(self, api_key: str, workspace_id: str, user_id: str):
        super().__init__(api_key)
        self.workspace_id = workspace_id
        self.user_id = user_id

    def get_time_entries(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """
        Get time entries for the current user

        Args:
            start_date: Start date for filtering entries
            end_date: End date for filtering entries

        Returns:
            List of time entries
        """
        params = {}
        if start_date:
            params["start"] = format_date(start_date)
        if end_date:
            params["end"] = format_date(end_date)

        endpoint = f"workspaces/{self.workspace_id}/user/{self.user_id}/time-entries"
        return self._request("GET", endpoint, params=params)

    def start_timer(self, description: str, project_id: Optional[str] = None,
                    task_id: Optional[str] = None, tag_ids: List[str] = None) -> Dict:
        """
        Start a new timer

        Args:
            description: Description of the time entry
            project_id: Optional project ID to associate with entry
            task_id: Optional task ID to associate with entry
            tag_ids: Optional list of tag IDs to associate with entry

        Returns:
            Time entry data
        """
        data = {
            "start": get_current_utc_time(),
            "description": description,
            "billable": "false"
        }

        if project_id:
            data["projectId"] = project_id
        if task_id:
            data["taskId"] = task_id
        if tag_ids:
            data["tagIds"] = tag_ids

        endpoint = f"workspaces/{self.workspace_id}/time-entries"
        return self._request("POST", endpoint, data=data)

    def stop_timer(self) -> Dict:
        """
        Stop the current running timer

        Returns:
            Updated time entry data
        """
        endpoint = f"workspaces/{self.workspace_id}/user/{self.user_id}/time-entries"
        data = {
            "end": get_current_utc_time()
        }
        return self._request("PATCH", endpoint, data=data)

    def add_time_entry(self, start_time: datetime, end_time: datetime, description: str,
                       project_id: Optional[str] = None, task_id: Optional[str] = None,
                       tag_ids: List[str] = None) -> Dict:
        """
        Add a manual time entry

        Args:
            start_time: Start time of the entry
            end_time: End time of the entry
            description: Description of what was worked on
            project_id: Optional project ID to associate with entry
            task_id: Optional task ID to associate with entry
            tag_ids: Optional list of tag IDs to associate with entry

        Returns:
            Time entry data
        """
        data = {
            "start": format_date(start_time),
            "end": format_date(end_time),
            "description": description,
            "billable": "false"
        }

        if project_id:
            data["projectId"] = project_id
        if task_id:
            data["taskId"] = task_id
        if tag_ids:
            data["tagIds"] = tag_ids

        endpoint = f"workspaces/{self.workspace_id}/time-entries"
        return self._request("POST", endpoint, data=data) 