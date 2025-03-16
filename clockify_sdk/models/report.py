from typing import Dict, List
from datetime import datetime
from ..base.client import ClockifyClient
from ..utils.date_utils import format_date

class ReportManager(ClockifyClient):
    """Handles report generation in Clockify"""

    def __init__(self, api_key: str, workspace_id: str):
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def generate_report(self, start_date: datetime, end_date: datetime,
                        project_ids: List[str] = None, user_ids: List[str] = None) -> Dict:
        """
        Generate a time report

        Args:
            start_date: Start date for the report
            end_date: End date for the report
            project_ids: Optional list of project IDs to filter by
            user_ids: Optional list of user IDs to filter by

        Returns:
            Report data
        """
        data = {
            "dateRangeStart": format_date(start_date),
            "dateRangeEnd": format_date(end_date),
            "summaryFilter": {
                "groups": ["PROJECT", "USER"]
            }
        }

        if project_ids:
            data["projectIds"] = project_ids
        if user_ids:
            data["userIds"] = user_ids

        endpoint = f"workspaces/{self.workspace_id}/reports/summary"
        return self._request("POST", endpoint, data=data, is_reports=True) 