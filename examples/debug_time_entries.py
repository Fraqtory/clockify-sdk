#!/usr/bin/env python3
"""
Debug script to list all time entries for a specific project and report type.
This script demonstrates the debugging functionality without requiring interactive input.
"""

import os
from datetime import datetime, timezone, timedelta
from clockify_sdk import Clockify
from clockify_sdk.exceptions import ClockifyError

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def debug_time_entries():
    """Debug function to list all time entries for debugging purposes."""
    
    # Initialize the client
    api_key = os.getenv("CLOCKIFY_API_KEY")
    if not api_key:
        print("Please set CLOCKIFY_API_KEY environment variable")
        return
    
    client = Clockify(api_key=api_key)
    
    try:
        # Get all projects
        projects = client.projects.get_all()
        if not projects:
            print("No projects found.")
            return
        
        print(f"Found {len(projects)} projects.")
        
        # Find a project that has time entries by checking all projects
        print(f"\nChecking all {len(projects)} projects for time entries...")
        
        # Test with a few different projects to find one with entries
        test_projects = projects[:5]  # Test first 5 projects
        
        for project in test_projects:
            project_id = project.get('id')
            project_name = project.get('name', 'Unknown')
            
            print(f"\nTesting with project: {project_name} (ID: {project_id})")
            
            # Quick test to see if this project has any recent entries
            try:
                from datetime import datetime, timezone, timedelta
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=7)
                
                test_entries = client.reports.get_detailed_all_pages(
                    start=start_date,
                    end=end_date,
                    project_ids=[project_id],
                    page_size=100
                )
                
                if test_entries:
                    print(f"✅ Found {len(test_entries)} entries for {project_name}")
                    # Use this project for detailed testing
                    break
                else:
                    print(f"❌ No entries found for {project_name}")
                    
            except Exception as e:
                print(f"❌ Error testing {project_name}: {e}")
        else:
            print("No projects with time entries found in the last 7 days.")
            return
        
        # Test different date ranges
        test_cases = [
            {
                "name": "Last 7 Days",
                "start": datetime.now(timezone.utc) - timedelta(days=7),
                "end": datetime.now(timezone.utc)
            },
            {
                "name": "Current Week (Monday to Now)",
                "start": get_week_start(datetime.now(timezone.utc)),
                "end": datetime.now(timezone.utc)
            },
            {
                "name": "Last Month",
                "start": get_last_month_start(),
                "end": get_last_month_end()
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{'='*60}")
            print(f"DEBUGGING: {test_case['name']}")
            print(f"Date range: {test_case['start'].strftime('%Y-%m-%d %H:%M:%S')} to {test_case['end'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            try:
                # Get time entries with pagination
                print("Fetching time entries with pagination...")
                time_entries = client.reports.get_detailed_all_pages(
                    start=test_case['start'],
                    end=test_case['end'],
                    project_ids=[project_id],
                    page_size=1000
                )
                
                if not time_entries:
                    print("No time entries found for this project in the specified period.")
                    continue
                
                # Debug: Show all project IDs in the time entries
                project_ids_in_entries = set(entry.get('projectId') for entry in time_entries if entry.get('projectId'))
                print(f"DEBUG: Project IDs found in time entries: {list(project_ids_in_entries)}")
                print(f"DEBUG: Looking for project ID: {project_id}")
                
                # Filter to project-specific entries
                project_time_entries = [
                    entry for entry in time_entries 
                    if entry.get('projectId') == project_id
                ]
                
                print(f"Found {len(project_time_entries)} time entries for this project (filtered from {len(time_entries)} total entries).")
                
                # Show a few sample entries to see the structure
                if time_entries:
                    print("DEBUG: Sample time entry structure:")
                    sample_entry = time_entries[0]
                    for key, value in sample_entry.items():
                        print(f"  {key}: {value}")
                    print()
                
                # Debug: List all time entries
                debug_list_time_entries(project_time_entries, test_case['name'])
                
            except ClockifyError as e:
                print(f"Error fetching time entries for {test_case['name']}: {e}")
        
    except ClockifyError as e:
        print(f"Error: {e}")

def debug_list_time_entries(time_entries, report_type):
    """Debug method to list all time entries for a specific report."""
    print(f"\n=== DEBUG: All Time Entries for {report_type} ===")
    print(f"Total entries: {len(time_entries)}")
    print("-" * 80)
    
    for i, entry in enumerate(time_entries, 1):
        # Extract key information
        user_id = entry.get('userId', 'Unknown')
        project_id = entry.get('projectId', 'Unknown')
        task_id = entry.get('taskId', 'No task')
        description = entry.get('description', 'No description')
        duration = entry.get('duration', 0)
        start_time = entry.get('timeInterval', {}).get('start', 'Unknown')
        end_time = entry.get('timeInterval', {}).get('end', 'Unknown')
        billable = entry.get('billable', False)
        
        # Convert duration to hours
        hours = duration / 3600 if duration else 0
        
        print(f"Entry {i}:")
        print(f"  User ID: {user_id}")
        print(f"  Project ID: {project_id}")
        print(f"  Task ID: {task_id}")
        print(f"  Description: {description}")
        print(f"  Duration: {duration}s ({hours:.2f}h)")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        print(f"  Billable: {billable}")
        print("-" * 40)
    
    print(f"=== END DEBUG: {report_type} ===\n")

def get_week_start(date):
    """Get the start of the week (Monday) for a given date."""
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)

def get_last_month_start():
    """Get the start of last month."""
    today = datetime.now(timezone.utc)
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - timedelta(days=1)
    return last_month.replace(day=1)

def get_last_month_end():
    """Get the end of last month."""
    today = datetime.now(timezone.utc)
    first_of_this_month = today.replace(day=1)
    return first_of_this_month - timedelta(seconds=1)

if __name__ == "__main__":
    debug_time_entries()
