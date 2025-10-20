"""
Example script demonstrating minimum hours tracking functionality.

This script shows how to configure and use the minimum hours tracking feature
in the Clockify SDK project detail reporter.

Usage:
    python minimum_hours_example.py              # Interactive mode
    python minimum_hours_example.py --list-users # List all Clockify users with IDs
"""

import os
import sys
from clockify_sdk import Clockify

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def list_clockify_users():
    """List all users in the Clockify workspace with their IDs and names."""
    api_key = os.getenv("CLOCKIFY_API_KEY")
    workspace_id = os.getenv("CLOCKIFY_WORKSPACE_ID")
    
    if not api_key:
        print("Error: Please set CLOCKIFY_API_KEY in your environment variables.")
        return
    
    try:
        # Initialize Clockify client
        client = Clockify(api_key=api_key, workspace_id=workspace_id)
        
        print("CLOCKIFY USERS LIST")
        print("=" * 50)
        
        users = client.users.get_all()
        if users:
            print(f"\nFound {len(users)} users in your workspace:")
            print("-" * 50)
            for user in users:
                user_id = user.get('id', 'Unknown ID')
                user_name = user.get('name', 'Unknown Name')
                user_email = user.get('email', 'No email')
                status = "Active" if user.get('status') == 'ACTIVE' else "Inactive"
                print(f"ID: {user_id}")
                print(f"Name: {user_name}")
                print(f"Email: {user_email}")
                print(f"Status: {status}")
                print("-" * 50)
            
            print("\nTo configure minimum hours, update developer_minimums.json with:")
            print("the user IDs shown above and your desired minimum_weekly_hours.")
            print("\nExample configuration:")
            print("{")
            for i, user in enumerate(users[:3]):  # Show first 3 users as example
                user_id = user.get('id', 'user_id')
                user_name = user.get('name', 'User Name')
                print(f'  "{user_id}": {{')
                print(f'    "name": "{user_name}",')
                print(f'    "minimum_weekly_hours": 40')
                print(f'  }}{"," if i < 2 else ""}')
            print("}")
        else:
            print("No users found in your workspace.")
            
    except Exception as e:
        print(f"Error fetching users: {e}")
        print("Make sure you have proper permissions to view users and a valid API key.")

def main():
    """Demonstrate minimum hours tracking."""
    
    # Get API key from environment
    api_key = os.getenv("CLOCKIFY_API_KEY")
    workspace_id = os.getenv("CLOCKIFY_WORKSPACE_ID")
    
    if not api_key:
        print("Error: Please set CLOCKIFY_API_KEY in your environment variables.")
        return
    
    print("Minimum Hours Tracking Example")
    print("=" * 40)
    print()
    print("This example demonstrates the minimum hours tracking feature.")
    print("Developers who don't meet their minimum weekly hours will be")
    print("marked with a 🔴 emoji in the reports.")
    print()
    print("Configuration is stored in 'developer_minimums.json'")
    print("Example configuration:")
    print("""
{
  "user_id_1": {
    "name": "John Doe", 
    "minimum_weekly_hours": 40
  },
  "user_id_2": {
    "name": "Jane Smith",
    "minimum_weekly_hours": 35
  }
}
    """)
    print()
    print("To use this feature:")
    print("1. Update developer_minimums.json with your team's user IDs and minimum hours")
    print("2. Run the project_detail.py script")
    print("3. Generate reports - non-compliant developers will show 🔴 prefix")
    print()
    print("The system automatically calculates expected minimums for:")
    print("- Weekly reports: Uses the configured weekly minimum")
    print("- Monthly reports: Calculates based on number of weeks in the month")
    print("- Partial periods: Pro-rates the minimum based on time covered")
    
    # Ask user if they want to list users
    print("\n" + "="*60)
    print("OPTIONS:")
    print("1. List all Clockify users (to get their IDs for configuration)")
    print("2. Continue with full demonstration")
    print("="*60)
    
    choice = input("\nEnter your choice (1 or 2, or press Enter for option 2): ").strip()
    
    if choice == "1":
        print("\nListing Clockify users...")
        list_clockify_users()
        return
    
    # Initialize the reporter to show configuration loading
    try:
        from project_detail import ProjectDetailReporter
        reporter = ProjectDetailReporter(api_key, workspace_id)
        print()
        print("Configuration loaded successfully!")
        print("You can now run the main project_detail.py script to generate reports.")
        
        # List all users to help with configuration
        print("\n" + "="*60)
        print("CLOCKIFY USERS (for developer_minimums.json configuration)")
        print("="*60)
        
        try:
            users = reporter.client.users.get_all()
            if users:
                print(f"\nFound {len(users)} users in your workspace:")
                print("-" * 60)
                for user in users:
                    user_id = user.get('id', 'Unknown ID')
                    user_name = user.get('name', 'Unknown Name')
                    user_email = user.get('email', 'No email')
                    status = "Active" if user.get('status') == 'ACTIVE' else "Inactive"
                    print(f"ID: {user_id}")
                    print(f"Name: {user_name}")
                    print(f"Email: {user_email}")
                    print(f"Status: {status}")
                    print("-" * 60)
                
                print("\nTo configure minimum hours, update developer_minimums.json with:")
                print("the user IDs shown above and your desired minimum_weekly_hours.")
                print("\nExample configuration:")
                print("{")
                for i, user in enumerate(users[:3]):  # Show first 3 users as example
                    user_id = user.get('id', 'user_id')
                    user_name = user.get('name', 'User Name')
                    print(f'  "{user_id}": {{')
                    print(f'    "name": "{user_name}",')
                    print(f'    "minimum_weekly_hours": 40')
                    print(f'  }}{"," if i < 2 else ""}')
                print("}")
            else:
                print("No users found in your workspace.")
        except Exception as e:
            print(f"Error fetching users: {e}")
            print("Make sure you have proper permissions to view users.")
            
    except Exception as e:
        print(f"Error initializing reporter: {e}")

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list-users":
            # Direct user listing mode
            list_clockify_users()
        elif sys.argv[1] in ["--help", "-h"]:
            print("Minimum Hours Tracking Example")
            print("=" * 40)
            print()
            print("Usage:")
            print("  python minimum_hours_example.py              # Interactive mode")
            print("  python minimum_hours_example.py --list-users # List all Clockify users with IDs")
            print("  python minimum_hours_example.py --help      # Show this help")
            print()
            print("This script helps you configure minimum hours tracking by:")
            print("1. Listing all users in your Clockify workspace with their IDs")
            print("2. Showing example configuration for developer_minimums.json")
            print("3. Demonstrating the minimum hours tracking feature")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help to see available options.")
    else:
        # Interactive mode
        main()
