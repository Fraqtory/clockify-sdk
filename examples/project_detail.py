"""
Project Detail Script for Clockify SDK

This script provides an interactive interface to:
1. List all projects and allow user selection
2. Generate weekly reports (total hours, per-person breakdown with tasks and daily hours)
3. Generate monthly reports (total hours, per-person breakdown with weekly averages and billable hours)
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from clockify_sdk import Clockify
from clockify_sdk.exceptions import ClockifyError

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass


class ProjectDetailReporter:
    """Interactive project detail reporter for Clockify projects."""

    def __init__(self, api_key: str, workspace_id: Optional[str] = None):
        """
        Initialize the reporter.
        
        Args:
            api_key: Clockify API key
            workspace_id: Optional workspace ID to use
        """
        self.client = Clockify(api_key=api_key, workspace_id=workspace_id)
        print(f"Connected to Clockify workspace: {self.client.workspace_id}")
        
        # Load minimum hours configuration
        self.minimum_hours_config = self._load_minimum_hours_config()

    def run(self) -> None:
        """Main execution flow - runs in infinite loop until user types 'exit'."""
        print("Welcome to Clockify Project Detail Reporter!")
        print("Type 'exit' at any time to quit the program.\n")
        
        current_project_id = None
        current_project_name = None
        
        while True:
            try:
                # If no project selected, select one
                if not current_project_id:
                    project_id, project_name = self._select_project()
                    if not project_id:
                        print("No project selected. Returning to main menu.\n")
                        continue
                    current_project_id = project_id
                    current_project_name = project_name
                    print(f"\nSelected project: {current_project_name}")

                # Show project menu
                self._show_project_menu(current_project_name)
                choice = input("\nSelect an option: ").strip()
                
                if choice.lower() == 'exit':
                    print("Goodbye!")
                    break
                elif choice == '1':
                    self._generate_weekly_report(current_project_id, current_project_name)
                elif choice == '2':
                    self._generate_current_week_report(current_project_id, current_project_name)
                elif choice == '3':
                    self._generate_monthly_report(current_project_id, current_project_name)
                elif choice == '4':
                    self._generate_this_month_report(current_project_id, current_project_name)
                elif choice == '5':
                    self._generate_all_projects_monthly_report()
                elif choice == '6':
                    self._generate_all_projects_this_month_report()
                elif choice == '7':
                    # Change project
                    current_project_id = None
                    current_project_name = None
                    print("\nProject selection reset. Choose a new project.\n")
                    continue
                else:
                    print("Invalid choice. Please select 1, 2, 3, 4, 5, 6, 7, or type 'exit'.")
                    continue
                
                print("\n" + "="*60)
                print("Report completed! You can generate another report for the same project.")
                print("="*60 + "\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except ClockifyError as e:
                print(f"Clockify API error: {e}")
                print("Please try again.\n")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                print("Please try again.\n")

    def _show_project_menu(self, project_name: str) -> None:
        """Show the project menu with options."""
        print(f"\n📊 Project: {project_name}")
        print("-" * 50)
        print("1. Generate Weekly Report (Last Week Monday-Sunday)")
        print("2. Generate Current Week Report (Monday to Now)")
        print("3. Generate Monthly Report")
        print("4. Generate This Month Report (First Day to Now)")
        print("5. Generate All Projects Monthly Report (Last Month)")
        print("6. Generate All Projects This Month Report (Ongoing Month)")
        print("7. Change Project")
        print("Type 'exit' to quit")

    def _select_project(self) -> Tuple[Optional[str], Optional[str]]:
        """Display all projects and let user select one."""
        try:
            projects = self.client.projects.get_all()
            
            if not projects:
                print("No projects found in your workspace.")
                return None, None

            print("\nAvailable Projects:")
            print("-" * 50)
            for i, project in enumerate(projects, 1):
                name = project.get('name', 'Unknown')
                status = "Archived" if project.get('isArchived', False) else "Active"
                print(f"{i}. {name} ({status})")

            while True:
                try:
                    choice = input(f"\nSelect a project (1-{len(projects)}): ").strip()
                    if not choice:
                        return None, None
                    
                    index = int(choice) - 1
                    if 0 <= index < len(projects):
                        selected_project = projects[index]
                        return selected_project.get('id'), selected_project.get('name')
                    else:
                        print(f"Please enter a number between 1 and {len(projects)}")
                except ValueError:
                    print("Please enter a valid number")
                except KeyboardInterrupt:
                    return None, None

        except ClockifyError as e:
            print(f"Error fetching projects: {e}")
            return None, None


    def _generate_weekly_report(self, project_id: str, project_name: str) -> None:
        """Generate weekly report for the selected project (last week Monday-Sunday)."""
        print(f"\nGenerating Weekly Report for: {project_name}")
        print("=" * 60)

        # Calculate date range (last week)
        current_date = datetime.now(timezone.utc)
        start_date = self._get_last_week_start(current_date)
        end_date = self._get_last_week_end(current_date)

        try:
            # Get project team members first
            project_users = []
            project_user_ids = []
            
            try:
                project_users = self.client.projects.get_users(project_id)
                if project_users:
                    print(f"Found {len(project_users)} team members in this project.")
                    project_user_ids = [user.get('userId') for user in project_users if user.get('userId')]
                else:
                    print("No team members found for this project.")
            except ClockifyError as e:
                print(f"Could not get project team members: {e}")
                print("Will show all users who have time entries for this project.")

            # Get detailed report data (always filter by project)
            # Use pagination to get ALL entries for the week
            print("Fetching all time entries with pagination...")
            time_entries = self.client.reports.get_detailed_all_pages(
                start=start_date,
                end=end_date,
                project_ids=[project_id],
                page_size=1000
            )
            
            if not time_entries:
                print("No time entries found for this project in the last week.")
                return

            # Filter time entries to only include those for this specific project
            project_time_entries = [
                entry for entry in time_entries 
                if entry.get('projectId') == project_id
            ]
            
            if not project_time_entries:
                print("No time entries found for this specific project in the last week.")
                return

            print(f"Found {len(project_time_entries)} time entries for this project (filtered from {len(time_entries)} total entries).")
            
            # Check if we might have hit pagination limits
            if len(time_entries) >= 1000:
                print("⚠️  WARNING: Found 1000+ entries. Some data might be missing due to pagination limits.")
                print("   Consider using a smaller page size or implementing proper pagination.")
            
            # Debug: Show details of time entries
            total_debug_hours = 0
            miguel_entries = []
            for i, entry in enumerate(project_time_entries):
                duration = self._calculate_duration(entry)
                hours = duration / 3600
                total_debug_hours += hours
                start_time = entry.get('timeInterval', {}).get('start', 'N/A')
                user_id = entry.get('userId', 'Unknown')
                
            

            # Extract unique user IDs from project time entries
            project_worker_ids = list(set(entry.get('userId') for entry in project_time_entries if entry.get('userId')))
            print(f"Found {len(project_worker_ids)} users who worked on this project.")

            # Process the data
            team_data = self._process_weekly_data(project_time_entries, project_users)
            
            
            # Display the report
            self._display_weekly_report(team_data, start_date, end_date)

        except ClockifyError as e:
            print(f"Error generating weekly report: {e}")

    def _generate_current_week_report(self, project_id: str, project_name: str) -> None:
        """Generate report for the current week starting Monday."""
        print(f"\nGenerating Current Week Report for: {project_name}")
        print("=" * 60)

        # Calculate date range (current week starting Monday)
        # Use start of day to ensure we get all entries from the beginning of the day
        current_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = self._get_week_start(current_date)
        end_date = current_date  # Up to start of today

        try:
            # Get project team members first
            project_users = []
            project_user_ids = []
            
            try:
                project_users = self.client.projects.get_users(project_id)
                if project_users:
                    print(f"Found {len(project_users)} team members in this project.")
                    project_user_ids = [user.get('userId') for user in project_users if user.get('userId')]
                else:
                    print("No team members found for this project.")
            except ClockifyError as e:
                print(f"Could not get project team members: {e}")
                print("Will show all users who have time entries for this project.")

            # Get detailed report data (always filter by project)
            # Use larger page size to get all entries for the week
            # Use pagination to get ALL entries
            print("Fetching all time entries with pagination...")
            time_entries = self.client.reports.get_detailed_all_pages(
                start=start_date,
                end=end_date,
                project_ids=[project_id],
                page_size=1000
            )
            if not time_entries:
                print("No time entries found for this project in the current week.")
                return

            # Filter time entries to only include those for this specific project
            project_time_entries = [
                entry for entry in time_entries 
                if entry.get('projectId') == project_id
            ]
            
            if not project_time_entries:
                print("No time entries found for this specific project in the current week.")
                return

            print(f"Found {len(project_time_entries)} time entries for this project (filtered from {len(time_entries)} total entries).")


            # Extract unique user IDs from project time entries
            project_worker_ids = list(set(entry.get('userId') for entry in project_time_entries if entry.get('userId')))
            print(f"Found {len(project_worker_ids)} users who worked on this project.")

            # Process the data
            team_data = self._process_weekly_data(project_time_entries, project_users)
            
            # Display the report
            self._display_current_week_report(team_data, start_date, end_date)

        except ClockifyError as e:
            print(f"Error generating current week report: {e}")

    def _generate_monthly_report(self, project_id: str, project_name: str) -> None:
        """Generate monthly report for the selected project."""
        print(f"\nGenerating Monthly Report for: {project_name}")
        print("=" * 60)

        # Calculate date range (last month)
        start_date, end_date = self._get_last_month_range()

        try:
            # Get project team members first
            project_users = []
            project_user_ids = []
            
            try:
                project_users = self.client.projects.get_users(project_id)
                if project_users:
                    print(f"Found {len(project_users)} team members in this project.")
                    project_user_ids = [user.get('userId') for user in project_users if user.get('userId')]
                else:
                    print("No team members found for this project.")
            except ClockifyError as e:
                print(f"Could not get project team members: {e}")
                print("Will show all users who have time entries for this project.")

            # Get detailed report data (always filter by project)
            # Use pagination to get ALL entries
            print("Fetching all time entries with pagination...")
            time_entries = self.client.reports.get_detailed_all_pages(
                start=start_date,
                end=end_date,
                project_ids=[project_id],
                page_size=1000
            )
            if not time_entries:
                print("No time entries found for this project in the last month.")
                return

            # Filter time entries to only include those for this specific project
            project_time_entries = [
                entry for entry in time_entries 
                if entry.get('projectId') == project_id
            ]
            
            if not project_time_entries:
                print("No time entries found for this specific project in the last month.")
                return

            print(f"Found {len(project_time_entries)} time entries for this project (filtered from {len(time_entries)} total entries).")


            # Extract unique user IDs from project time entries
            project_worker_ids = list(set(entry.get('userId') for entry in project_time_entries if entry.get('userId')))
            print(f"Found {len(project_worker_ids)} users who worked on this project.")

            # Process the data
            team_data = self._process_monthly_data(project_time_entries, project_users)
            
            # Display the report
            self._display_monthly_report(team_data, start_date, end_date)

        except ClockifyError as e:
            print(f"Error generating monthly report: {e}")
            print(f"Date range: {start_date} to {end_date}")
            print(f"Project ID: {project_id}")
            print("This might be due to API rate limits, invalid project ID, or date range issues.")

    def _generate_this_month_report(self, project_id: str, project_name: str) -> None:
        """Generate report for this month (first day to current day)."""
        print(f"\nGenerating This Month Report for: {project_name}")
        print("=" * 60)

        # Calculate date range (this month from first day to current day)
        current_date = datetime.now(timezone.utc)
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            # Get project team members first
            project_users = []
            project_user_ids = []
            
            try:
                project_users = self.client.projects.get_users(project_id)
                if project_users:
                    print(f"Found {len(project_users)} team members in this project.")
                    project_user_ids = [user.get('userId') for user in project_users if user.get('userId')]
                else:
                    print("No team members found for this project.")
            except ClockifyError as e:
                print(f"Could not get project team members: {e}")
                print("Will show all users who have time entries for this project.")

            # Get detailed report data (always filter by project)
            # Use pagination to get ALL entries
            print("Fetching all time entries with pagination...")
            time_entries = self.client.reports.get_detailed_all_pages(
                start=start_date,
                end=end_date,
                project_ids=[project_id],
                page_size=1000
            )
            if not time_entries:
                print("No time entries found for this project in this month.")
                return

            # Filter time entries to only include those for this specific project
            project_time_entries = [
                entry for entry in time_entries 
                if entry.get('projectId') == project_id
            ]
            
            
            if not project_time_entries:
                print("No time entries found for this specific project in this month.")
                return

            print(f"Found {len(project_time_entries)} time entries for this project (filtered from {len(time_entries)} total entries).")


            # Extract unique user IDs from project time entries
            project_worker_ids = list(set(entry.get('userId') for entry in project_time_entries if entry.get('userId')))
            print(f"Found {len(project_worker_ids)} users who worked on this project.")

            # Process the data
            team_data = self._process_weekly_data(project_time_entries, project_users)
            
            # Display the report
            self._display_this_month_report(team_data, start_date, end_date)

        except ClockifyError as e:
            print(f"Error generating this month report: {e}")
            print(f"Date range: {start_date} to {end_date}")
            print(f"Project ID: {project_id}")
            print("This might be due to API rate limits, invalid project ID, or date range issues.")

    def _generate_all_projects_monthly_report(self) -> None:
        """Generate monthly report for all projects with color-coded indicators."""
        print(f"\nGenerating All Projects Monthly Report")
        print("=" * 60)

        # Calculate date range (last month)
        start_date, end_date = self._get_last_month_range()

        try:
            # Get all projects
            projects = self.client.projects.get_all()
            
            if not projects:
                print("No projects found in your workspace.")
                return

            print(f"Found {len(projects)} projects. Analyzing monthly hours...")
            print("=" * 60)

            project_hours = []
            
            for project in projects:
                project_id = project.get('id')
                project_name = project.get('name', 'Unknown Project')
                is_archived = project.get('isArchived', False)
                
                if is_archived:
                    continue  # Skip archived projects
                
                try:
                    # Get time entries for this project for the last month
                    time_entries = self.client.reports.get_detailed_all_pages(
                        start=start_date,
                        end=end_date,
                        project_ids=[project_id],
                        page_size=1000
                    )
                    
                    # Calculate total hours for this project
                    total_seconds = 0
                    for entry in time_entries:
                        if entry.get('projectId') == project_id:
                            total_seconds += self._calculate_duration(entry)
                    
                    total_hours = total_seconds / 3600
                    
                    # Determine emoji based on hours
                    if total_hours < 100:
                        emoji = "🔴"
                    elif total_hours <= 200:
                        emoji = "🟠"
                    else:
                        emoji = "🟢"
                    
                    # Only include projects with hours > 0
                    if total_hours > 0:
                        project_hours.append({
                            'name': project_name,
                            'hours': total_hours,
                            'emoji': emoji
                        })
                    
                except ClockifyError as e:
                    print(f"Error fetching data for project '{project_name}': {e}")
                    continue

            # Sort projects by hours (descending)
            project_hours.sort(key=lambda x: x['hours'], reverse=True)
            
            # Display the report
            self._display_all_projects_monthly_report(project_hours, start_date, end_date)

        except ClockifyError as e:
            print(f"Error generating all projects monthly report: {e}")

    def _display_all_projects_monthly_report(self, project_hours: List[Dict], start_date: datetime, end_date: datetime) -> None:
        """Display formatted all projects monthly report."""
        print(f"\nAll Projects Monthly Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("=" * 80)
        print("Legend: 🔴 < 100h | 🟠 100-200h | 🟢 > 200h")
        print("=" * 80)

        total_all_hours = 0
        
        for project in project_hours:
            name = project['name']
            hours = project['hours']
            emoji = project['emoji']
            total_all_hours += hours
            
            print(f"{emoji} {name}: {hours:.2f}h")

        print("=" * 80)
        print(f"📊 Total Hours Across All Projects: {total_all_hours:.2f}h")
        print(f"📈 Average Hours Per Project: {total_all_hours/len(project_hours):.2f}h")
        print(f"📅 Report Period: {start_date.strftime('%B %Y')}")
        
        # Summary by category
        red_count = sum(1 for p in project_hours if p['emoji'] == '🔴')
        orange_count = sum(1 for p in project_hours if p['emoji'] == '🟠')
        green_count = sum(1 for p in project_hours if p['emoji'] == '🟢')
        
        print(f"\n📊 Summary:")
        print(f"   🔴 Projects under 100h: {red_count}")
        print(f"   🟠 Projects 100-200h: {orange_count}")
        print(f"   🟢 Projects over 200h: {green_count}")

    def _generate_all_projects_this_month_report(self) -> None:
        """Generate this month report for all projects with color-coded indicators."""
        print(f"\nGenerating All Projects This Month Report")
        print("=" * 60)

        # Calculate date range (this month from first day to current day)
        current_date = datetime.now(timezone.utc)
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            # Get all projects
            projects = self.client.projects.get_all()
            
            if not projects:
                print("No projects found in your workspace.")
                return

            print(f"Found {len(projects)} projects. Analyzing this month's hours...")
            print("=" * 60)

            project_hours = []
            
            for project in projects:
                project_id = project.get('id')
                project_name = project.get('name', 'Unknown Project')
                is_archived = project.get('isArchived', False)
                
                if is_archived:
                    continue  # Skip archived projects
                
                try:
                    # Get time entries for this project for this month
                    time_entries = self.client.reports.get_detailed_all_pages(
                        start=start_date,
                        end=end_date,
                        project_ids=[project_id],
                        page_size=1000
                    )
                    
                    # Calculate total hours for this project
                    total_seconds = 0
                    for entry in time_entries:
                        if entry.get('projectId') == project_id:
                            total_seconds += self._calculate_duration(entry)
                    
                    total_hours = total_seconds / 3600
                    
                    # Determine emoji based on hours
                    if total_hours < 100:
                        emoji = "🔴"
                    elif total_hours <= 200:
                        emoji = "🟠"
                    else:
                        emoji = "🟢"
                    
                    # Only include projects with hours > 0
                    if total_hours > 0:
                        project_hours.append({
                            'name': project_name,
                            'hours': total_hours,
                            'emoji': emoji
                        })
                    
                except ClockifyError as e:
                    print(f"Error fetching data for project '{project_name}': {e}")
                    continue

            # Sort projects by hours (descending)
            project_hours.sort(key=lambda x: x['hours'], reverse=True)
            
            # Display the report
            self._display_all_projects_this_month_report(project_hours, start_date, end_date)

        except ClockifyError as e:
            print(f"Error generating all projects this month report: {e}")

    def _display_all_projects_this_month_report(self, project_hours: List[Dict], start_date: datetime, end_date: datetime) -> None:
        """Display formatted all projects this month report."""
        print(f"\nAll Projects This Month Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("=" * 80)
        print("Legend: 🔴 < 100h | 🟠 100-200h | 🟢 > 200h")
        print("=" * 80)

        total_all_hours = 0
        
        for project in project_hours:
            name = project['name']
            hours = project['hours']
            emoji = project['emoji']
            total_all_hours += hours
            
            print(f"{emoji} {name}: {hours:.2f}h")

        print("=" * 80)
        print(f"📊 Total Hours Across All Projects: {total_all_hours:.2f}h")
        print(f"📈 Average Hours Per Project: {total_all_hours/len(project_hours):.2f}h")
        print(f"📅 Report Period: {start_date.strftime('%B %Y')} (Ongoing Month)")
        
        # Summary by category
        red_count = sum(1 for p in project_hours if p['emoji'] == '🔴')
        orange_count = sum(1 for p in project_hours if p['emoji'] == '🟠')
        green_count = sum(1 for p in project_hours if p['emoji'] == '🟢')
        
        print(f"\n📊 Summary:")
        print(f"   🔴 Projects under 100h: {red_count}")
        print(f"   🟠 Projects 100-200h: {orange_count}")
        print(f"   🟢 Projects over 200h: {green_count}")

    def _process_weekly_data(self, time_entries: List[Dict], project_users: List[Dict]) -> Dict:
        """Process time entries for weekly report."""
        team_data = {}
        
        
        # Create a mapping of user_id to user info from project users
        user_info_map = {}
        for user in project_users:
            user_id = user.get('userId')
            if user_id:
                user_info_map[user_id] = user
        
        processed_count = 0
        for i, entry in enumerate(time_entries):
            processed_count += 1
            user_id = entry.get('userId')
            if not user_id:
                continue

            # Initialize user data if not exists
            if user_id not in team_data:
                user_info = user_info_map.get(user_id, {})
                # If we don't have project user info, try to get user name from all users
                if not user_info:
                    user_name = self._get_user_name_from_all_users(user_id)
                else:
                    user_name = user_info.get('name', f'User {user_id[:8]}')
                    
                team_data[user_id] = {
                    'total_seconds': 0,
                    'tasks': {},
                    'daily_hours': {},
                    'daily_tasks': {},  # Track tasks per day
                    'user_name': user_name
                }

            # Calculate duration
            duration_seconds = self._calculate_duration(entry)
            team_data[user_id]['total_seconds'] += duration_seconds

            # Group by task
            task_id = entry.get('taskId')
            if task_id:
                task_name = self._get_task_name(task_id)
                if task_name not in team_data[user_id]['tasks']:
                    team_data[user_id]['tasks'][task_name] = 0
                team_data[user_id]['tasks'][task_name] += duration_seconds

            # Group by day
            start_time = entry.get('timeInterval', {}).get('start')
            if start_time:
                day = self._parse_date(start_time).strftime('%A')
                if day not in team_data[user_id]['daily_hours']:
                    team_data[user_id]['daily_hours'][day] = 0
                team_data[user_id]['daily_hours'][day] += duration_seconds
                
                # Track tasks per day
                if day not in team_data[user_id]['daily_tasks']:
                    team_data[user_id]['daily_tasks'][day] = {}
                
                task_id = entry.get('taskId')
                if task_id:
                    task_name = self._get_task_name(task_id)
                    if task_name not in team_data[user_id]['daily_tasks'][day]:
                        team_data[user_id]['daily_tasks'][day][task_name] = 0
                    team_data[user_id]['daily_tasks'][day][task_name] += duration_seconds

        
        return team_data

    def _process_monthly_data(self, time_entries: List[Dict], project_users: List[Dict]) -> Dict:
        """Process time entries for monthly report."""
        team_data = {}
        
        # Create a mapping of user_id to user info from project users
        user_info_map = {}
        for user in project_users:
            user_id = user.get('userId')
            if user_id:
                user_info_map[user_id] = user
        
        for entry in time_entries:
            user_id = entry.get('userId')
            if not user_id:
                continue

            # Initialize user data if not exists
            if user_id not in team_data:
                user_info = user_info_map.get(user_id, {})
                # If we don't have project user info, try to get user name from all users
                if not user_info:
                    user_name = self._get_user_name_from_all_users(user_id)
                else:
                    user_name = user_info.get('name', f'User {user_id[:8]}')
                    
                team_data[user_id] = {
                    'total_seconds': 0,
                    'billable_seconds': 0,
                    'weekly_totals': {},
                    'user_name': user_name
                }

            # Calculate duration
            duration_seconds = self._calculate_duration(entry)
            team_data[user_id]['total_seconds'] += duration_seconds

            # Track billable hours
            if entry.get('billable', False):
                team_data[user_id]['billable_seconds'] += duration_seconds

            # Group by week
            start_time = entry.get('timeInterval', {}).get('start')
            if start_time:
                date = self._parse_date(start_time)
                week_start = self._get_week_start(date)
                week_key = week_start.strftime('%Y-%m-%d')
                
                if week_key not in team_data[user_id]['weekly_totals']:
                    team_data[user_id]['weekly_totals'][week_key] = 0
                team_data[user_id]['weekly_totals'][week_key] += duration_seconds

        return team_data

    def _display_weekly_report(self, team_data: Dict, start_date: datetime, end_date: datetime) -> None:
        """Display formatted weekly report."""
        print(f"\nWeekly Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("=" * 80)

        total_team_hours = 0
        
        for user_id, data in team_data.items():
            user_name = data['user_name']
            total_hours = data['total_seconds'] / 3600
            total_team_hours += total_hours

            # Check compliance and get display prefix
            is_compliant, display_prefix = self._check_hours_compliance(user_id, total_hours, start_date, end_date)
            display_name = f"{display_prefix}{user_name}"

            print(f"\n👤 {display_name}")
            print(f"   Total Hours: {total_hours:.2f}h")
            
            # Show tasks
            if data['tasks']:
                print("   Tasks:")
                for task_name, task_seconds in data['tasks'].items():
                    task_hours = task_seconds / 3600
                    print(f"     • {task_name}: {task_hours:.2f}h")

        print(f"\n📊 Team Total: {total_team_hours:.2f} hours")
        
        # Add weekly summary
        print(f"\n📈 Weekly Summary:")
        print(f"   • Total Team Hours: {total_team_hours:.2f}h")
        print(f"   • Average Daily Hours: {total_team_hours/7:.2f}h (including weekends)")
        print(f"   • Report Period: {start_date.strftime('%A, %B %d')} to {end_date.strftime('%A, %B %d')}")
        print(f"   • Days Covered: Monday through Sunday (7 days)")
        
        # Ask if user wants to see daily breakdown
        self._ask_for_daily_breakdown(team_data, "weekly")

    def _display_current_week_report(self, team_data: Dict, start_date: datetime, end_date: datetime) -> None:
        """Display formatted current week report."""
        print(f"\nCurrent Week Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("=" * 80)

        total_team_hours = 0
        
        for user_id, data in team_data.items():
            user_name = data['user_name']
            total_hours = data['total_seconds'] / 3600
            total_team_hours += total_hours

            # Check compliance and get display prefix
            is_compliant, display_prefix = self._check_hours_compliance(user_id, total_hours, start_date, end_date)
            display_name = f"{display_prefix}{user_name}"

            print(f"\n👤 {display_name}")
            print(f"   Total Hours: {total_hours:.2f}h")
            
            # Show tasks
            if data['tasks']:
                print("   Tasks:")
                for task_name, task_seconds in data['tasks'].items():
                    task_hours = task_seconds / 3600
                    print(f"     • {task_name}: {task_hours:.2f}h")

        print(f"\n📊 Team Total: {total_team_hours:.2f} hours")
        
        # Add current week summary
        print(f"\n📈 Current Week Summary:")
        print(f"   • Total Team Hours: {total_team_hours:.2f}h")
        print(f"   • Average Daily Hours: {total_team_hours/7:.2f}h")
        print(f"   • Report Period: {start_date.strftime('%A, %B %d')} to {end_date.strftime('%A, %B %d')}")
        print(f"   • Type: Current week (Monday to now)")
        
        # Ask if user wants to see daily breakdown
        self._ask_for_daily_breakdown(team_data, "current week")


    def _display_monthly_report(self, team_data: Dict, start_date: datetime, end_date: datetime) -> None:
        """Display formatted monthly report."""
        print(f"\nMonthly Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("=" * 80)

        total_team_hours = 0
        
        for user_id, data in team_data.items():
            user_name = data['user_name']
            total_hours = data['total_seconds'] / 3600
            billable_hours = data.get('billable_seconds', 0) / 3600
            total_team_hours += total_hours

            # Calculate weekly average
            weekly_totals = list(data.get('weekly_totals', {}).values())
            weekly_average = sum(weekly_totals) / len(weekly_totals) / 3600 if weekly_totals else 0

            # Check compliance and get display prefix
            is_compliant, display_prefix = self._check_hours_compliance(user_id, total_hours, start_date, end_date)
            display_name = f"{display_prefix}{user_name}"

            print(f"\n👤 {display_name}")
            print(f"   Total Hours: {total_hours:.2f}h")
            print(f"   Billable Hours: {billable_hours:.2f}h")
            print(f"   Average Weekly Hours: {weekly_average:.2f}h")
            
            # Show weekly breakdown
            if data.get('weekly_totals'):
                print("   Weekly Breakdown:")
                for week, week_seconds in sorted(data['weekly_totals'].items()):
                    week_hours = week_seconds / 3600
                    print(f"     Week of {week}: {week_hours:.2f}h")

        print(f"\n📊 Team Total: {total_team_hours:.2f} hours")

    def _display_this_month_report(self, team_data: Dict, start_date: datetime, end_date: datetime) -> None:
        """Display formatted this month report."""
        print(f"\nThis Month Report: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("=" * 80)

        total_team_hours = 0
        
        for user_id, data in team_data.items():
            user_name = data['user_name']
            total_hours = data['total_seconds'] / 3600
            total_team_hours += total_hours

            # Check compliance and get display prefix
            is_compliant, display_prefix = self._check_hours_compliance(user_id, total_hours, start_date, end_date)
            display_name = f"{display_prefix}{user_name}"

            print(f"\n👤 {display_name}")
            print(f"   Total Hours: {total_hours:.2f}h")
            
            # Show tasks
            if data['tasks']:
                print("   Tasks:")
                for task_name, task_seconds in data['tasks'].items():
                    task_hours = task_seconds / 3600
                    print(f"     • {task_name}: {task_hours:.2f}h")

        print(f"\n📊 Team Total: {total_team_hours:.2f} hours")
        
        # Add this month summary
        print(f"\n📈 This Month Summary:")
        print(f"   • Total Team Hours: {total_team_hours:.2f}h")
        print(f"   • Report Period: {start_date.strftime('%B %d')} to {end_date.strftime('%B %d, %Y')}")
        print(f"   • Type: Current month (first day to now)")
        
        # Ask if user wants to see daily breakdown
        self._ask_for_daily_breakdown(team_data, "this month")

    def _calculate_duration(self, entry: Dict) -> int:
        """Calculate duration of a time entry in seconds."""
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
            start_dt = self._parse_date(start)
            end_dt = self._parse_date(end)
            return int((end_dt - start_dt).total_seconds())
        except (ValueError, TypeError):
            return 0

    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO 8601 date string to datetime object."""
        try:
            # Handle both Z and +00:00 timezone formats
            if date_str.endswith('Z'):
                date_str = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(date_str)
        except ValueError:
            # Fallback for other formats
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

    def _get_week_start(self, date: datetime) -> datetime:
        """Get the Monday of the week for a given date."""
        days_since_monday = date.weekday()
        return date - timedelta(days=days_since_monday)

    def _get_last_month_start(self, current_date: datetime) -> datetime:
        """Get the start of the previous month."""
        # Get the first day of the current month
        first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Subtract one day to get the last day of the previous month
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        
        # Get the first day of the previous month
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        return first_day_previous_month

    def _get_last_month_range(self) -> Tuple[datetime, datetime]:
        """Get the start and end dates of the previous month."""
        current_date = datetime.now(timezone.utc)
        
        # Get the first day of the current month
        first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Subtract one day to get the last day of the previous month
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        
        # Get the first day of the previous month
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        # Set end date to end of the last day of previous month
        end_date = last_day_previous_month.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return first_day_previous_month, end_date

    def _get_last_week_start(self, current_date: datetime) -> datetime:
        """Get the start of the previous week (Monday)."""
        # Get the start of the current week (Monday)
        current_week_start = self._get_week_start(current_date)
        
        # Subtract 7 days to get the start of the previous week
        last_week_start = current_week_start - timedelta(days=7)
        
        return last_week_start

    def _get_last_week_end(self, current_date: datetime) -> datetime:
        """Get the end of the previous week (Sunday)."""
        # Get the start of the current week (Monday)
        current_week_start = self._get_week_start(current_date)
        
        # Subtract 1 day to get the end of the previous week (Sunday)
        last_week_end = current_week_start - timedelta(days=1)
        
        # Set to end of Sunday
        last_week_end = last_week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return last_week_end

    def _get_user_name_from_all_users(self, user_id: str) -> str:
        """Get user name by ID from all users."""
        try:
            # Try to get from all users
            users = self.client.users.get_all()
            for user in users:
                if user.get('id') == user_id:
                    return user.get('name', f'User {user_id[:8]}')
            return f'User {user_id[:8]}'
        except:
            return f'User {user_id[:8]}'

    def _get_task_name(self, task_id: str) -> str:
        """Get task name by ID."""
        try:
            # This would require fetching task details
            # For now, return a generic name
            return f'Task {task_id[:8]}'
        except:
            return f'Task {task_id[:8]}'

    def _load_minimum_hours_config(self) -> Dict[str, Dict[str, any]]:
        """Load minimum hours configuration from JSON file."""
        # Try multiple possible paths for the config file
        possible_paths = [
            "developer_minimums.json",  # Current directory
            "../developer_minimums.json",  # Parent directory
            os.path.join(os.path.dirname(__file__), "..", "developer_minimums.json"),  # Project root
            os.path.join(os.path.dirname(__file__), "developer_minimums.json")  # Same directory as script
        ]
        
        for config_path in possible_paths:
            try:
                if os.path.exists(config_path):
                    print(f"Trying to load config from: {config_path}")
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        print(f"✅ Loaded minimum hours configuration for {len(config)} developers from {config_path}")
                        
                        return config
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
                continue
        
        print("❌ No minimum hours configuration found in any of the expected locations.")
        print("Expected locations:")
        for path in possible_paths:
            print(f"  - {path}")
        print("Proceeding without minimum hours tracking.")
        return {}

    def _check_hours_compliance(self, user_id: str, actual_hours: float, start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
        """
        Check if a developer meets their minimum hours requirement.
        
        Args:
            user_id: User ID to check
            actual_hours: Actual hours worked
            start_date: Start date of the report period
            end_date: End date of the report period
            
        Returns:
            Tuple of (is_compliant, display_prefix) where display_prefix is "🔴 " if not compliant, "" if compliant
        """

        # Check if user has minimum hours configured
        if user_id not in self.minimum_hours_config:
            return True, ""  # No minimum set, so always compliant
    

        user_config = self.minimum_hours_config[user_id]
        minimum_weekly_hours = user_config.get('minimum_weekly_hours', 0)
        
        if minimum_weekly_hours <= 0:
            return True, ""  # No minimum set, so always compliant
        
        # Calculate expected minimum based on the time period
        from clockify_sdk.utils.date_utils import count_weeks_in_range
        weeks_in_period = count_weeks_in_range(start_date, end_date)
        expected_minimum = minimum_weekly_hours * weeks_in_period
        
        
        # Check compliance
        is_compliant = actual_hours >= expected_minimum
        
        if is_compliant:
            return True, ""
        else:
            return False, "🔴 "

    def _ask_for_daily_breakdown(self, team_data: Dict, report_type: str) -> None:
        """Ask user if they want to see daily breakdown and display it if requested."""
        print(f"\n" + "="*60)
        print("📅 DAILY BREAKDOWN OPTION")
        print("="*60)
        
        while True:
            choice = input(f"\nWould you like to see the daily breakdown for this {report_type} report? (y/n): ").strip().lower()
            
            if choice in ['y', 'yes']:
                self._display_daily_breakdown(team_data)
                break
            elif choice in ['n', 'no']:
                print("Daily breakdown skipped.")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    def _display_daily_breakdown(self, team_data: Dict) -> None:
        """Display daily breakdown for all users."""
        print(f"\n📅 Daily Breakdown")
        print("=" * 60)
        
        for user_id, data in team_data.items():
            user_name = data['user_name']
            print(f"\n👤 {user_name}")
            
            # Show daily breakdown with tasks
            print("   Daily Breakdown:")
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days_order:
                # Always show all days, even if 0 hours
                day_hours = data['daily_hours'].get(day, 0) / 3600
                print(f"     {day}: {day_hours:.2f}h")
                
                # Show tasks for this day if any
                if day in data.get('daily_tasks', {}) and data['daily_tasks'][day]:
                    for task_name, task_seconds in data['daily_tasks'][day].items():
                        task_hours = task_seconds / 3600
                        print(f"       • {task_name}: {task_hours:.2f}h")


def main():
    """Main execution function."""
    # Get API key from environment variables
    api_key = os.getenv("CLOCKIFY_API_KEY")
    workspace_id = os.getenv("CLOCKIFY_WORKSPACE_ID")  # Optional

    if not api_key:
        print("Error: No API key found. Please set CLOCKIFY_API_KEY in your .env file.")
        return

    try:
        # Initialize reporter
        reporter = ProjectDetailReporter(api_key, workspace_id)
        reporter.run()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
