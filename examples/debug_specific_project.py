#!/usr/bin/env python3
"""
Debug script to test with a specific project that has time entries.
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

def debug_specific_project():
    """Debug function to test with a project that has actual time entries."""
    
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
        
        # Test with a project that we know has entries (CourtMaster AI)
        # Based on the debug output, we saw projectName: "CourtMaster AI"
        target_project = None
        for project in projects:
            if "CourtMaster" in project.get('name', ''):
                target_project = project
                break
        
        if not target_project:
            print("CourtMaster project not found, using first project")
            target_project = projects[0]
        
        project_id = target_project.get('id')
        project_name = target_project.get('name', 'Unknown')
        
        print(f"\nTesting with project: {project_name} (ID: {project_id})")
        
        # Test different date ranges
        test_cases = [
            {
                "name": "Last 7 Days",
                "start": datetime.now(timezone.utc) - timedelta(days=7),
                "end": datetime.now(timezone.utc)
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
                
                print(f"DEBUG: Total entries fetched: {len(time_entries)}")
                
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
                
                # Show detailed info for each entry
                if project_time_entries:
                    print(f"\n=== DETAILED TIME ENTRIES ===")
                    for i, entry in enumerate(project_time_entries, 1):
                        user_id = entry.get('userId', 'Unknown')
                        duration = entry.get('duration', 0)
                        description = entry.get('description', 'No description')
                        start_time = entry.get('timeInterval', {}).get('start', 'Unknown')
                        end_time = entry.get('timeInterval', {}).get('end', 'Unknown')
                        hours = duration / 3600 if duration else 0
                        
                        print(f"Entry {i}:")
                        print(f"  User: {user_id}")
                        print(f"  Description: {description}")
                        print(f"  Duration: {duration}s ({hours:.2f}h)")
                        print(f"  Start: {start_time}")
                        print(f"  End: {end_time}")
                        print("-" * 40)
                    
                    # Test the processing logic
                    print(f"\n=== TESTING PROCESSING LOGIC ===")
                    test_processing_logic(project_time_entries)
                
            except ClockifyError as e:
                print(f"Error fetching time entries for {test_case['name']}: {e}")
        
    except ClockifyError as e:
        print(f"Error: {e}")

def test_processing_logic(time_entries):
    """Test the processing logic to see if any entries are being skipped."""
    print(f"Testing processing logic with {len(time_entries)} entries...")
    
    total_seconds = 0
    processed_count = 0
    
    for i, entry in enumerate(time_entries):
        processed_count += 1
        print(f"Processing entry {i+1}/{len(time_entries)}: User={entry.get('userId')}")
        
        # Calculate duration
        duration = entry.get('duration', 0)
        if duration:
            total_seconds += duration
            print(f"  Duration: {duration}s ({duration/3600:.2f}h)")
        else:
            print(f"  Duration: 0s (missing duration field)")
        
        print(f"  Running total: {total_seconds}s ({total_seconds/3600:.2f}h)")
        print("-" * 30)
    
    print(f"\nFINAL RESULTS:")
    print(f"Processed {processed_count} entries")
    print(f"Total seconds: {total_seconds}")
    print(f"Total hours: {total_seconds/3600:.2f}")

if __name__ == "__main__":
    debug_specific_project()
