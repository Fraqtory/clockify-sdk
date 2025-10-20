"""
Advanced usage example for the Clockify SDK

This example demonstrates more advanced usage patterns for the Clockify SDK,
including error handling, analytics, and reporting.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from dotenv import load_dotenv

from clockify_sdk import Clockify
from clockify_sdk.exceptions import ClockifyError, RateLimitError
from clockify_sdk.logging import logger

# Load environment variables from .env file
load_dotenv()


class ClockifyAnalytics:
    """Example class demonstrating advanced SDK usage."""

    def __init__(self, api_key: str, workspace_id: Optional[str] = None):
        """
        Initialize the analytics class.
        Args:
            api_key: Clockify API key
            workspace_id: Optional workspace ID to use. If not provided,
                          the first available workspace will be used.
        """
        logger.info("Initializing Clockify Analytics...")
        self.client = Clockify(api_key=api_key, workspace_id=workspace_id)

        # If no workspace_id was provided, log the selected one
        if not workspace_id and self.client.workspace_id:
            logger.info(f"Using workspace ID: {self.client.workspace_id}")

    def get_project_stats(self, project_id: str, days: int = 30) -> Dict:
        """
        Get statistics for a specific project.
        Args:
            project_id: ID of the project to analyze
            days: Number of days to analyze (default: 30)
        Returns:
            Dictionary with project statistics
        """
        logger.info(f"Analyzing project {project_id} for the last {days} days...")

        try:
            # Get project details
            project = self.client.projects.get_by_id(project_id)
            logger.info(f"Project: {project.get('name')}")

            # Get time entries for the specified period
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            # Format dates in ISO 8601 format
            # start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            # end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            time_entries = self.client.time_entries.get_by_user_id(
                user_id=self.client.user_id,
                project_ids=[project_id],
                start=start_date,
                end=end_date,
            )

            # Calculate statistics
            total_seconds = sum(
                self._calculate_duration(entry) for entry in time_entries
            )
            unique_users = len(
                {entry.get("userId") for entry in time_entries if entry.get("userId")}
            )

            stats = {
                "project_name": project.get("name", "Unknown"),
                "total_seconds": total_seconds,
                "total_hours": round(total_seconds / 3600, 2),
                "unique_users": unique_users,
                "entry_count": len(time_entries),
                "period": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d"),
                },
            }

            logger.info(
                f"Project stats: {stats['total_hours']} hours across {stats['unique_users']} users"
            )
            return stats

        except RateLimitError:
            logger.warning("Rate limit exceeded, waiting before retry...")
            # In a real application, implement exponential backoff here
            raise
        except ClockifyError as e:
            logger.error(f"Error getting project stats: {e}")
            raise

    def get_team_productivity(self, days: int = 7) -> List[Dict]:
        """
        Get productivity metrics for the team.
        Args:
            days: Number of days to analyze (default: 7)
        Returns:
            List of dictionaries with user productivity stats
        """
        logger.info(f"Analyzing team productivity for the last {days} days...")

        try:
            # Get all users
            users = self.client.users.get_all()
            logger.info(f"Found {len(users)} users")

            # Get time entries for the specified period
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            # Format dates in ISO 8601 format
            # start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            # end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            team_stats = []
            for user in users:
                user_id = user.get("id")
                user_name = user.get("name", "Unknown")

                if not user_id:
                    continue

                logger.info(f"Analyzing productivity for user: {user_name}")

                time_entries = self.client.time_entries.get_by_user_id(
                    user_id=user_id, start=start_date, end=end_date
                )

                total_seconds = sum(
                    self._calculate_duration(entry) for entry in time_entries
                )

                # Get unique projects
                project_ids = {
                    entry.get("projectId")
                    for entry in time_entries
                    if entry.get("projectId")
                }

                user_stats = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "total_seconds": total_seconds,
                    "total_hours": round(total_seconds / 3600, 2),
                    "project_count": len(project_ids),
                    "entry_count": len(time_entries),
                }

                team_stats.append(user_stats)
                logger.info(
                    f"User {user_name}: {user_stats['total_hours']} hours "
                    f"across {user_stats['project_count']} projects"
                )

            return team_stats

        except ClockifyError as e:
            logger.error(f"Error getting team productivity: {e}")
            raise

    def generate_weekly_report(self) -> Dict:
        """
        Generate a comprehensive weekly report.
        Returns:
            Dictionary with report data
        """
        logger.info("Generating weekly report...")

        try:
            # Get date range for last week
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)

            # Get all users
            users = self.client.users.get_all()
            logger.info(f"Found {len(users)} users")

            # Get time entries for the specified period
            time_entries = []
            for user in users:
                user_id = user.get("id")
                if user_id:
                    entries = self.client.time_entries.get_by_user_id(
                        user_id=user_id, start=start_date, end=end_date
                    )
                    time_entries.extend(entries)

            # Calculate total hours and other stats
            total_seconds = sum(
                self._calculate_duration(entry) for entry in time_entries
            )
            unique_projects = {
                entry.get("projectId")
                for entry in time_entries
                if entry.get("projectId")
            }
            unique_users = {
                entry.get("userId") for entry in time_entries if entry.get("userId")
            }

            # Create the report
            weekly_report = {
                "period": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d"),
                },
                "total_seconds": total_seconds,
                "total_hours": round(total_seconds / 3600, 2),
                "project_count": len(unique_projects),
                "user_count": len(unique_users),
                "entry_count": len(time_entries),
            }

            logger.info(
                f"Weekly report: {weekly_report['total_hours']} hours across "
                f"{weekly_report['project_count']} projects by {weekly_report['user_count']} users"
            )

            return weekly_report

        except ClockifyError as e:
            logger.error(f"Error generating weekly report: {e}")
            raise

    @staticmethod
    def _calculate_duration(entry: Dict) -> int:
        """
        Calculate the duration of a time entry in seconds.
        Args:
            entry: Time entry dictionary
        Returns:
            Duration in seconds
        """
        # If the entry has a duration field, use it
        if entry.get("duration"):
            return entry["duration"]

        # Otherwise, calculate from timeInterval
        time_interval = entry.get("timeInterval", {})
        start = time_interval.get("start")
        end = time_interval.get("end")

        if not start or not end:
            return 0

        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            return int((end_dt - start_dt).total_seconds())
        except (ValueError, TypeError):
            return 0


def main():
    """Run the advanced usage example."""
    # Get API key from environment variables
    api_key = os.getenv("CLOCKIFY_API_KEY")
    workspace_id = os.getenv("CLOCKIFY_WORKSPACE_ID")  # Optional

    if not api_key:
        logger.error("No API key found. Please set CLOCKIFY_API_KEY in your .env file.")
        return

    try:
        # Initialize analytics with workspace ID if provided
        analytics = ClockifyAnalytics(api_key, workspace_id)

        # Get all projects
        projects = analytics.client.projects.get_all()

        if not projects:
            logger.warning("No projects found. Please create a project in Clockify.")
            return

        # Analyze the first project
        for project in projects:
            project_id = project.get("id")
            if project_id:
                logger.info("\n=== Project Analysis ===")
                project_stats = analytics.get_project_stats(project_id)
                logger.info(f"Project stats: {project_stats}")
            # Get team productivity
            logger.info("\n=== Team Productivity ===")
            team_stats = analytics.get_team_productivity()
            logger.info(f"Team stats: {team_stats}")

            # Generate weekly report
            logger.info("\n=== Weekly Report ===")
            weekly_report = analytics.generate_weekly_report()
            logger.info(f"Weekly report: {weekly_report}")

    except ClockifyError as e:
        logger.error(f"Clockify API error: {e}")
        if hasattr(e, "status_code"):
            logger.error(f"Status code: {e.status_code}")
        if hasattr(e, "response"):
            logger.error(f"Response: {e.response}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
