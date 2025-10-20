"""
Report model for the Clockify SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from ..utils.date_utils import format_datetime
from .base import ClockifyBaseModel


class Report(ClockifyBaseModel):
    """Report model representing a Clockify report."""

    id: str = Field(..., description="Report ID")
    name: str = Field(..., description="Report name")
    workspace_id: str = Field(..., description="Workspace ID")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    project_ids: List[str] = Field(
        default_factory=list, description="List of project IDs"
    )
    user_ids: List[str] = Field(default_factory=list, description="List of user IDs")
    task_ids: List[str] = Field(default_factory=list, description="List of task IDs")
    tag_ids: List[str] = Field(default_factory=list, description="List of tag IDs")
    billable: Optional[bool] = Field(
        None, description="Whether to include billable time entries"
    )
    description: Optional[str] = Field(None, description="Report description")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )
    date_range_start: str = Field(..., description="Start date in datetime format")
    date_range_end: str = Field(..., description="End date in datetime format")
    amount_shown: Optional[str] = Field(
        None, description="Enum: EARNED, COST, PROFIT, HIDE_AMOUNT, EXPORT"
    )
    amounts: List[str] = Field(default_factory=list, description="Array of amounts")
    approval_state: Optional[str] = Field(
        None, description="Enum: APPROVED, UNAPPROVED, ALL"
    )
    archived: Optional[bool] = Field(
        None, description="Indicates whether the report is archived"
    )


class ReportSummary(ClockifyBaseModel):
    """Model representing a summary report from Clockify."""

    totals: List[Dict[str, Any]] = Field(
        default_factory=list, description="Summary totals"
    )
    groups: List[Dict[str, Any]] = Field(
        default_factory=list, description="Grouped data"
    )


class ReportManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for report-related operations."""

    def get_summary(
        self,
        start: datetime,
        end: datetime,
        user_ids: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        group_by: Optional[List[str]] = None,
        sort_column: str = "GROUP",
    ) -> Dict[str, Any]:
        """Get a summary of the report.

        Args:
            start: Start date
            end: End date
            user_ids: Optional list of user IDs to filter by
            project_ids: Optional list of project IDs to filter by
            group_by: List of fields to group by (PROJECT, CLIENT, TAG, etc.)
            sort_column: Column to sort by

        Returns:
            Summary of the report
        """

        data = {
            "dateRangeStart": format_datetime(start),
            "dateRangeEnd": format_datetime(end),
            "summaryFilter": {
                "groups": group_by,
                "sortColumn": sort_column,
            },
            "exportType": "JSON",
        }

        if user_ids:
            data["userIds"] = user_ids

        if project_ids:
            data["projectIds"] = project_ids

        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/reports/summary",
            json=data,
            response_type=Dict[str, Any],
            is_reports=True,
        )

    def get_detailed(
        self,
        start: datetime,
        end: datetime,
        user_ids: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        page_size: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Get detailed report data.

        Args:
            start: Start date
            end: End date
            user_ids: Optional list of user IDs to filter by
            project_ids: Optional list of project IDs to filter by
            page_size: Number of results per page
            page: Page number

        Returns:
            Detailed report data
        """

        data = {
            "dateRangeStart": format_datetime(start),
            "dateRangeEnd": format_datetime(end),
            "detailedFilter": {
                "page": page,
                "pageSize": page_size,
                "sortColumn": "DATE",
            },
            "exportType": "JSON",
            "projects": {
                "ids": project_ids
            }
        }

        if user_ids:
            data["userIds"] = user_ids

        print("Loading ...")

        return self._request(
            "POST",
            f"workspaces/{self.workspace_id}/reports/detailed",
            json=data,
            response_type=Dict[str, Any],
            is_reports=True,
        )

    def get_detailed_all_pages(
        self,
        start: datetime,
        end: datetime,
        user_ids: Optional[List[str]] = None,
        project_ids: Optional[List[str]] = None,
        page_size: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get all detailed report data across all pages.
        
        This method automatically handles pagination to fetch all time entries
        for the given date range, which is essential for accurate monthly reports.

        Args:
            start: Start date
            end: End date
            user_ids: Optional list of user IDs to filter by
            project_ids: Optional list of project IDs to filter by
            page_size: Number of results per page (max 1000)

        Returns:
            List of all time entries across all pages
        """
        all_time_entries = []
        page = 1
        
        while True:
            try:
                report_data = self.get_detailed(
                    start=start,
                    end=end,
                    user_ids=user_ids,
                    project_ids=project_ids,
                    page_size=page_size,
                    page=page
                )
                
                time_entries = report_data.get('timeentries', [])
                if not time_entries:
                    break
                    
                all_time_entries.extend(time_entries)
                
                # If we got fewer entries than page_size, we've reached the end
                if len(time_entries) < page_size:
                    break
                    
                page += 1
                
            except Exception as e:
                # Log the error but don't fail completely
                print(f"Warning: Error fetching page {page}: {e}")
                break
                
        return all_time_entries

    def get_monthly_report_data(
        self,
        project_id: str,
        year: int,
        month: int,
    ) -> Dict[str, Any]:
        """Get complete monthly report data for a specific project and month.
        
        This method provides a convenient way to get all time entries for a
        specific month, handling pagination automatically.

        Args:
            project_id: ID of the project
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Dictionary containing all time entries and metadata for the month
        """
        from ..utils.date_utils import get_month_range
        
        # Get the first and last day of the month
        first_day, last_day = get_month_range(year, month)
        
        # Get all time entries for the month
        time_entries = self.get_detailed_all_pages(
            start=first_day,
            end=last_day,
            project_ids=[project_id]
        )
        
        return {
            'timeentries': time_entries,
            'start_date': first_day,
            'end_date': last_day,
            'project_id': project_id,
            'total_entries': len(time_entries)
        }

    def get_weekly_report_data(
        self,
        project_id: str,
        year: int,
        week: int,
    ) -> Dict[str, Any]:
        """Get complete weekly report data for a specific project and week.
        
        This method provides a convenient way to get all time entries for a
        specific week, handling pagination automatically.

        Args:
            project_id: ID of the project
            year: Year (e.g., 2024)
            week: Week number (1-53)

        Returns:
            Dictionary containing all time entries and metadata for the week
        """
        from ..utils.date_utils import get_week_range
        
        # Get the start and end of the specified week
        week_start, week_end = get_week_range(year, week)
        
        # Get all time entries for the week
        time_entries = self.get_detailed_all_pages(
            start=week_start,
            end=week_end,
            project_ids=[project_id]
        )
        
        return {
            'timeentries': time_entries,
            'start_date': week_start,
            'end_date': week_end,
            'project_id': project_id,
            'total_entries': len(time_entries)
        }
