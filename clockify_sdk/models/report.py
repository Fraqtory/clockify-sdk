"""
Report model for the Clockify SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class Report(ClockifyBaseModel):
    """Report model representing a Clockify report."""

    id: str = Field(..., description="Report ID")
    name: str = Field(..., description="Report name")
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
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


class ReportManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for report-related operations."""

    def get_all(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all reports in a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of reports
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/reports",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, workspace_id: str, report_id: str) -> Dict[str, Any]:
        """Get a specific report by ID.

        Args:
            workspace_id: ID of the workspace
            report_id: ID of the report

        Returns:
            Report information
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/reports/{report_id}",
            response_type=Dict[str, Any],
        )

    def create(self, workspace_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report.

        Args:
            workspace_id: ID of the workspace
            report: Report data

        Returns:
            Created report information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/reports",
            json=report,
            response_type=Dict[str, Any],
        )

    def update(
        self, workspace_id: str, report_id: str, report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing report.

        Args:
            workspace_id: ID of the workspace
            report_id: ID of the report
            report: Updated report data

        Returns:
            Updated report information
        """
        return self._request(
            "PUT",
            f"workspaces/{workspace_id}/reports/{report_id}",
            json=report,
            response_type=Dict[str, Any],
        )

    def delete(self, workspace_id: str, report_id: str) -> None:
        """Delete a report.

        Args:
            workspace_id: ID of the workspace
            report_id: ID of the report
        """
        self._request(
            "DELETE",
            f"workspaces/{workspace_id}/reports/{report_id}",
            response_type=Dict[str, Any],
        )
