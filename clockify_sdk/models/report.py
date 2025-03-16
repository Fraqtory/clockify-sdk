"""
Report model and manager for Clockify API
"""
from datetime import datetime
from typing import Dict, List, Optional

from ..base.client import ClockifyBaseClient
from ..utils.date_utils import format_datetime


class ReportManager(ClockifyBaseClient):
    """Manager for Clockify report operations"""

    def __init__(self, api_key: str, workspace_id: str):
        """
        Initialize the report manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime,
        project_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a detailed report

        Args:
            start_date: Report start date
            end_date: Report end date
            project_ids: Optional list of project IDs to filter by

        Returns:
            Report object containing time entries and summary
        """
        data = {
            "dateRangeStart": format_datetime(start_date),
            "dateRangeEnd": format_datetime(end_date),
            "detailedFilter": {
                "page": 1,
                "pageSize": 1000
            }
        }

        if project_ids:
            data["detailedFilter"]["projectIds"] = project_ids

        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/reports/detailed",
            data=data,
            is_reports=True
        ) 