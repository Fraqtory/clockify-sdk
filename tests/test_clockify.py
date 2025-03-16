import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from clockify_sdk import Clockify

# Mock responses for different API calls
MOCK_USER = {
    "id": "user123",
    "email": "test@example.com",
    "name": "Test User"
}

MOCK_WORKSPACE = {
    "id": "workspace123",
    "name": "Test Workspace"
}

MOCK_CLIENT = {
    "id": "client123",
    "name": "Test Client",
    "address": "Test Address"
}

MOCK_PROJECT = {
    "id": "project123",
    "name": "Test Project",
    "clientId": "client123"
}

MOCK_TASK = {
    "id": "task123",
    "name": "Test Task",
    "projectId": "project123",
    "status": "ACTIVE"
}

MOCK_TIME_ENTRY = {
    "id": "entry123",
    "description": "Test Entry",
    "timeInterval": {
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-01T01:00:00Z",
        "duration": "PT1H"
    }
}

@pytest.fixture
def mock_clockify():
    """Create a Clockify instance with mocked API calls"""
    with patch('clockify_sdk.base.client.ClockifyClient._request') as mock_request:
        # Configure mock responses
        def mock_response(*args, **kwargs):
            method = args[0]
            endpoint = args[1]
            
            if endpoint == "user":
                return MOCK_USER
            elif "workspaces" in endpoint and method == "GET":
                return [MOCK_WORKSPACE]
            elif "clients" in endpoint:
                return MOCK_CLIENT
            elif "projects" in endpoint:
                return MOCK_PROJECT
            elif "tasks" in endpoint:
                return MOCK_TASK if method != "POST" else [MOCK_TASK]
            elif "time-entries" in endpoint:
                return MOCK_TIME_ENTRY
            elif "reports" in endpoint:
                return {"totals": [{"totalTime": 3600}]}
            
            return {}

        mock_request.side_effect = mock_response
        clockify = Clockify(api_key="test_api_key")
        return clockify

def test_user_management(mock_clockify):
    """Test user management functionality"""
    user = mock_clockify.user_manager.get_current_user()
    assert user["id"] == MOCK_USER["id"]
    assert user["email"] == MOCK_USER["email"]

def test_client_management(mock_clockify):
    """Test client management functionality"""
    # Create client
    client = mock_clockify.clients.create_client(
        name="Test Client",
        address="Test Address"
    )
    assert client["id"] == MOCK_CLIENT["id"]
    assert client["name"] == MOCK_CLIENT["name"]

    # Get client
    client = mock_clockify.clients.get_client(client["id"])
    assert client["id"] == MOCK_CLIENT["id"]

def test_project_management(mock_clockify):
    """Test project management functionality"""
    # Create project
    project = mock_clockify.projects.create_project(
        name="Test Project",
        client_id=MOCK_CLIENT["id"]
    )
    assert project["id"] == MOCK_PROJECT["id"]
    assert project["name"] == MOCK_PROJECT["name"]

def test_task_management(mock_clockify):
    """Test task management functionality"""
    # Create task
    task = mock_clockify.tasks.create_task(
        project_id=MOCK_PROJECT["id"],
        name="Test Task"
    )
    assert task["id"] == MOCK_TASK["id"]
    assert task["name"] == MOCK_TASK["name"]

    # Bulk create tasks
    tasks = mock_clockify.tasks.bulk_create_tasks(
        project_id=MOCK_PROJECT["id"],
        tasks=[{"name": "Task 1"}, {"name": "Task 2"}]
    )
    assert len(tasks) == 1  # Mock returns single task
    assert tasks[0]["id"] == MOCK_TASK["id"]

    # Mark task as done
    task = mock_clockify.tasks.mark_task_done(
        project_id=MOCK_PROJECT["id"],
        task_id=MOCK_TASK["id"]
    )
    assert task["id"] == MOCK_TASK["id"]

def test_time_entry_management(mock_clockify):
    """Test time entry management functionality"""
    # Start timer
    entry = mock_clockify.time_entries.start_timer(
        description="Test Entry",
        project_id=MOCK_PROJECT["id"],
        task_id=MOCK_TASK["id"]
    )
    assert entry["id"] == MOCK_TIME_ENTRY["id"]
    assert entry["description"] == MOCK_TIME_ENTRY["description"]

    # Stop timer
    stopped = mock_clockify.time_entries.stop_timer()
    assert stopped["timeInterval"]["duration"] == "PT1H"

    # Add manual entry
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now()
    entry = mock_clockify.time_entries.add_time_entry(
        start_time=start_time,
        end_time=end_time,
        description="Manual Entry",
        project_id=MOCK_PROJECT["id"]
    )
    assert entry["id"] == MOCK_TIME_ENTRY["id"]

def test_report_generation(mock_clockify):
    """Test report generation functionality"""
    report = mock_clockify.reports.generate_report(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        project_ids=[MOCK_PROJECT["id"]]
    )
    assert "totals" in report
    assert report["totals"][0]["totalTime"] == 3600

def test_workspace_switching(mock_clockify):
    """Test workspace switching functionality"""
    new_workspace_id = "new_workspace123"
    mock_clockify.set_active_workspace(new_workspace_id)
    assert mock_clockify.workspace_id == new_workspace_id
    assert mock_clockify.user_manager.workspace_id == new_workspace_id
    assert mock_clockify.projects.workspace_id == new_workspace_id
    assert mock_clockify.tasks.workspace_id == new_workspace_id
    assert mock_clockify.time_entries.workspace_id == new_workspace_id 