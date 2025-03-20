"""
Basic usage example for the Clockify SDK

This example demonstrates how to use the Clockify SDK for basic operations.
"""

import os

from dotenv import load_dotenv

from clockify_sdk import Clockify
from clockify_sdk.exceptions import ClockifyError
from clockify_sdk.logging import logger

# Load environment variables from .env file
load_dotenv()


def main():
    """Run the basic usage example."""
    # Get API key from environment variables
    api_key = os.getenv("CLOCKIFY_API_KEY")
    if not api_key:
        logger.error("No API key found. Please set CLOCKIFY_API_KEY in your .env file.")
        return

    # Initialize the Clockify client
    logger.info("Initializing Clockify client...")
    client = Clockify(api_key=api_key)

    try:
        # Get all workspaces
        logger.info("Fetching workspaces...")
        workspaces = client.get_workspaces()
        logger.info(f"Found {len(workspaces)} workspaces")

        if not workspaces:
            logger.warning(
                "No workspaces found. Please create a workspace in Clockify."
            )
            return

        # Display workspace information
        for workspace in workspaces:
            logger.info(
                f"Workspace: {workspace.get('name')} (ID: {workspace.get('id')})"
            )

        # Get all projects in the workspace
        logger.info("\nFetching projects...")
        projects = client.projects.get_all()
        logger.info(f"Found {len(projects)} projects")

        # Display project information
        for project in projects:
            logger.info(f"Project: {project.get('name')} (ID: {project.get('id')})")

        # Get time entries for the last week
        logger.info("\nFetching time entries for the last week...")

        # Get time entries using the correct parameters
        time_entries = client.time_entries.get_all_in_progress()
        logger.info(f"Found {len(time_entries)} time entries")

        # Display time entry information
        for entry in time_entries[:5]:  # Show only the first 5 entries
            start_time = entry.get("timeInterval", {}).get("start", "")
            description = entry.get("description", "No description")
            project_id = entry.get("projectId", "No project")
            logger.info(
                f"Entry: {description} - Started: {start_time} - Project ID: {project_id}"
            )

        if len(time_entries) > 5:
            logger.info(f"... and {len(time_entries) - 5} more entries")

    except ClockifyError as e:
        logger.error(f"Clockify API error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
