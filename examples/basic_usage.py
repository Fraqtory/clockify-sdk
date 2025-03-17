"""
Basic usage examples for the Clockify SDK
"""

import os
from datetime import datetime, timedelta, timezone

from clockify_sdk import Clockify
from clockify_sdk.logging import logger


def main():
    # Initialize the client
    # You can either provide the API key directly or set it in the environment
    api_key = os.getenv("CLOCKIFY_API_KEY")
    if not api_key:
        return

    client = Clockify(api_key=api_key)

    try:
        # Get all workspaces
        logger.info("Fetching workspaces...")
        workspaces = client.get_workspaces()
        for _workspace in workspaces:
            pass

        # Set active workspace (using first workspace)
        if workspaces:
            workspace_id = workspaces[0]["id"]
            client.set_active_workspace(workspace_id)
            logger.info(f"Set active workspace to: {workspaces[0]['name']}")

        # Get all projects
        logger.info("\nFetching projects...")
        projects = client.projects.get_all()
        for _project in projects:
            pass

        # Get time entries for the last week
        logger.info("\nFetching time entries...")
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        time_entries = client.time_entries.get_all(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        for _entry in time_entries:
            pass

        # Generate a report
        logger.info("\nGenerating report...")
        client.reports.generate(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            project_ids=[p["id"] for p in projects],
        )

    except Exception as e:
        logger.error(f"An error occurred: {e!s}")
        raise


if __name__ == "__main__":
    main()
