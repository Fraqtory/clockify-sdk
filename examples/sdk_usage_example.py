"""
Example usage of the enhanced Clockify SDK with new report functions.

This example demonstrates how to use the new SDK functions that solve
the pagination and date range issues in reports.
"""

import os
from clockify_sdk import Clockify
from clockify_sdk.utils.date_utils import get_last_month_range, get_last_week_range

def main():
    """Demonstrate the new SDK functionality."""
    
    # Initialize the client
    api_key = os.getenv("CLOCKIFY_API_KEY")
    if not api_key:
        print("Please set CLOCKIFY_API_KEY environment variable")
        return
    
    client = Clockify(api_key=api_key)
    
    # Example 1: Get last month's report with automatic pagination
    print("=== Last Month Report (with pagination) ===")
    project_id = "your-project-id"  # Replace with actual project ID
    
    try:
        # This automatically handles pagination and gets ALL time entries
        monthly_data = client.get_last_month_report(project_id)
        
        print(f"Found {monthly_data['total_entries']} time entries")
        print(f"Date range: {monthly_data['start_date']} to {monthly_data['end_date']}")
        
        # Process the data
        total_hours = sum(entry.get('duration', 0) for entry in monthly_data['timeentries']) / 3600
        print(f"Total hours: {total_hours:.2f}")
        
    except Exception as e:
        print(f"Error getting monthly report: {e}")
    
    # Example 2: Get last week's report
    print("\n=== Last Week Report (with pagination) ===")
    
    try:
        weekly_data = client.get_last_week_report(project_id)
        
        print(f"Found {weekly_data['total_entries']} time entries")
        print(f"Date range: {weekly_data['start_date']} to {weekly_data['end_date']}")
        
        # Process the data
        total_hours = sum(entry.get('duration', 0) for entry in weekly_data['timeentries']) / 3600
        print(f"Total hours: {total_hours:.2f}")
        
    except Exception as e:
        print(f"Error getting weekly report: {e}")
    
    # Example 3: Get specific month report
    print("\n=== Specific Month Report (December 2024) ===")
    
    try:
        december_data = client.reports.get_monthly_report_data(
            project_id=project_id,
            year=2024,
            month=12
        )
        
        print(f"Found {december_data['total_entries']} time entries for December 2024")
        
    except Exception as e:
        print(f"Error getting December report: {e}")
    
    # Example 4: Get all pages manually
    print("\n=== Manual Pagination Example ===")
    
    try:
        from datetime import datetime, timezone
        
        # Get last month's date range
        start_date, end_date = get_last_month_range()
        
        # Get all time entries with automatic pagination
        all_entries = client.reports.get_detailed_all_pages(
            start=start_date,
            end=end_date,
            project_ids=[project_id]
        )
        
        print(f"Retrieved {len(all_entries)} time entries with automatic pagination")
        
    except Exception as e:
        print(f"Error with manual pagination: {e}")
    
    # Example 5: Using date utilities directly
    print("\n=== Date Utilities Example ===")
    
    try:
        # Get last month range
        start, end = get_last_month_range()
        print(f"Last month: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        
        # Get last week range
        start, end = get_last_week_range()
        print(f"Last week: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"Error with date utilities: {e}")

if __name__ == "__main__":
    main()



