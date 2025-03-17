"""
Advanced usage examples for the Clockify SDK
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from clockify_sdk import Clockify
from clockify_sdk.exceptions import ClockifyError, RateLimitError
from clockify_sdk.logging import logger


class ClockifyAnalytics:
    """Example class demonstrating advanced SDK usage"""

    def __init__(self, api_key: str):
        self.client = Clockify(api_key=api_key)
        self.workspace_id = self.client.get_workspaces()[0]["id"]
        self.client.set_active_workspace(self.workspace_id)

    def get_project_stats(self, project_id: str) -> Dict:
        """Get statistics for a specific project"""
        try:
            # Get project details
            project = self.client.projects.get(project_id)

            # Get time entries for the last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            time_entries = self.client.time_entries.get_all(
                project_id=project_id,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            # Calculate statistics
            total_time = sum(entry["duration"] for entry in time_entries)
            unique_users = len({entry["userId"] for entry in time_entries})

            return {
                "project_name": project["name"],
                "total_time": total_time,
                "unique_users": unique_users,
                "entry_count": len(time_entries),
            }

        except RateLimitError:
            logger.warning("Rate limit exceeded, waiting before retry...")
            # Implement exponential backoff here
            raise
        except ClockifyError as e:
            logger.error(f"Error getting project stats: {e.message}")
            raise

    def get_team_productivity(self, days: int = 7) -> List[Dict]:
        """Get productivity metrics for the team"""
        try:
            # Get all users
            users = self.client.user_manager.get_all()

            # Get time entries for the specified period
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            team_stats = []
            for user in users:
                time_entries = self.client.time_entries.get_all(
                    user_id=user["id"],
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                )

                total_time = sum(entry["duration"] for entry in time_entries)
                project_count = len({entry["projectId"] for entry in time_entries})

                team_stats.append(
                    {
                        "user_name": user["name"],
                        "total_time": total_time,
                        "project_count": project_count,
                        "entry_count": len(time_entries),
                    }
                )

            return team_stats

        except ClockifyError as e:
            logger.error(f"Error getting team productivity: {e.message}")
            raise

    def generate_weekly_report(self) -> Dict:
        """Generate a comprehensive weekly report"""
        try:
            # Get date range for last week
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)

            # Get all projects
            projects = self.client.projects.get_all()

            # Generate report for all projects
            report = self.client.reports.generate(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                project_ids=[p["id"] for p in projects],
            )

            # Get team productivity
            team_stats = self.get_team_productivity(days=7)

            return {
                "period": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d"),
                },
                "total_time": report["totalTime"],
                "project_count": len(projects),
                "team_stats": team_stats,
            }

        except ClockifyError as e:
            logger.error(f"Error generating weekly report: {e.message}")
            raise


def main():
    # Initialize analytics
    api_key = os.getenv("CLOCKIFY_API_KEY")
    if not api_key:
        return

    analytics = ClockifyAnalytics(api_key)

    try:
        # Get project statistics
        projects = analytics.client.projects.get_all()
        for project in projects:
            analytics.get_project_stats(project["id"])

        # Get team productivity
        team_stats = analytics.get_team_productivity()
        for _stat in team_stats:
            pass

        # Generate weekly report
        analytics.generate_weekly_report()

    except ClockifyError as e:
        logger.error(f"An error occurred: {e.message}")
        if hasattr(e, "status_code"):
            pass
        if hasattr(e, "response"):
            pass
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e!s}")
        raise


if __name__ == "__main__":
    main()
