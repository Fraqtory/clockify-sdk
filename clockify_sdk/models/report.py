"""Report management for Clockify API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from clockify_sdk.base.client import ClockifyBaseClient


class ReportManager(ClockifyBaseClient):
    """Manager for Clockify report operations"""

    def __init__(self, api_key: str, workspace_id: str) -> None:
        """
        Initialize the report manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_detailed_report(
        self,
        start_date: datetime,
        end_date: datetime,
        project_ids: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        client_ids: Optional[List[str]] = None,
        task_ids: Optional[List[str]] = None,
        tag_ids: Optional[List[str]] = None,
        include_time_entries: bool = True,
    ) -> Dict[str, Any]:
        """Get a detailed report.

        Args:
            start_date: Start date
            end_date: End date
            project_ids: Optional list of project IDs
            user_ids: Optional list of user IDs
            client_ids: Optional list of client IDs
            task_ids: Optional list of task IDs
            tag_ids: Optional list of tag IDs
            include_time_entries: Whether to include time entries

        Returns:
            Detailed report data
        """
        data: Dict[str, Any] = {
            "dateRangeStart": start_date.isoformat() + "Z",
            "dateRangeEnd": end_date.isoformat() + "Z",
            "detailedFilter": {
                "page": 1,
                "pageSize": 1000,
                "sortColumn": "DATE",
            },
            "exportType": "JSON",
        }

        if project_ids:
            data["detailedFilter"]["projectIds"] = project_ids
        if user_ids:
            data["detailedFilter"]["userIds"] = user_ids
        if client_ids:
            data["detailedFilter"]["clientIds"] = client_ids
        if task_ids:
            data["detailedFilter"]["taskIds"] = task_ids
        if tag_ids:
            data["detailedFilter"]["tagIds"] = tag_ids
        if not include_time_entries:
            data["detailedFilter"]["includeTimeEntries"] = False

        endpoint = f"workspaces/{self.workspace_id}/reports/detailed"
        return self._request("POST", endpoint, data=data, is_reports=True)
