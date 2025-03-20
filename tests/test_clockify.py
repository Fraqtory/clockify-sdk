"""Test cases for the Clockify SDK"""

from datetime import datetime, timedelta
from unittest import TestCase, mock

from clockify_sdk import Clockify


class TestClockify(TestCase):
    """Test cases for Clockify"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        self.workspace_id = "test-workspace-id"
        self.user_id = "test-user-id"
        self.project_id = "test-project-id"
        self.task_id = "test-task-id"
        self.time_entry_id = "test-time-entry-id"

        # Mock responses for user initialization
        self.mock_user = {"id": self.user_id, "email": "test@example.com"}
        self.mock_workspaces = [{"id": self.workspace_id, "name": "Test Workspace"}]
        self.mock_project = {"id": self.project_id, "name": "Test Project"}
        self.mock_task = {"id": self.task_id, "name": "Test Task"}
        self.mock_time_entry = {
            "id": self.time_entry_id,
            "description": "Test Time Entry",
            "timeInterval": {
                "start": "2024-03-20T10:00:00Z",
                "end": "2024-03-20T11:00:00Z",
            },
        }
        self.mock_running_time_entry = {
            "id": self.time_entry_id,
            "description": "Test Time Entry",
            "timeInterval": {
                "start": "2024-03-20T10:00:00Z",
                "end": None,
            },
        }

        # Create patcher for requests
        self.requests_patcher = mock.patch("clockify_sdk.connection.requests")
        self.mock_requests = self.requests_patcher.start()

        # Set up mock session
        self.mock_session = mock.Mock()
        self.mock_requests.Session.return_value = self.mock_session

        def mock_request(**kwargs):
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.ok = True

            # Return appropriate response based on the URL
            if kwargs["url"].endswith("/user"):
                mock_response.json.return_value = self.mock_user
            elif kwargs["url"].endswith("/workspaces"):
                mock_response.json.return_value = self.mock_workspaces
            elif kwargs["url"].endswith("/projects"):
                mock_response.json.return_value = [self.mock_project]
            elif kwargs["url"].endswith("/tasks"):
                mock_response.json.return_value = [self.mock_task]
            elif kwargs["url"].endswith("/time-entries"):
                if kwargs.get("method") == "POST":
                    mock_response.json.return_value = self.mock_running_time_entry
                else:
                    mock_response.json.return_value = [self.mock_time_entry]
            elif kwargs["url"].endswith(self.project_id):
                mock_response.json.return_value = self.mock_project
            elif kwargs["url"].endswith(self.time_entry_id):
                mock_response.json.return_value = self.mock_time_entry
            else:
                mock_response.status_code = 404
                mock_response.ok = False

            return mock_response

        self.mock_session.request.side_effect = mock_request

    def tearDown(self):
        """Clean up test fixtures"""
        self.requests_patcher.stop()

    def test_init(self):
        """Test initialization"""
        client = Clockify(self.api_key)
        self.assertEqual(client.api_key, self.api_key)
        self.assertEqual(client.workspace_id, self.workspace_id)
        self.assertEqual(client.user_id, self.user_id)

    def test_get_workspaces(self):
        """Test getting workspaces"""
        client = Clockify(self.api_key)
        workspaces = client.get_workspaces()
        self.assertEqual(workspaces, self.mock_workspaces)

    def test_get_projects(self):
        """Test getting projects"""
        client = Clockify(self.api_key)
        projects = client.projects.get_all()
        self.assertEqual(projects, [self.mock_project])

    def test_get_project(self):
        """Test getting a project"""
        client = Clockify(self.api_key)
        project = client.projects.get_by_id(self.project_id)
        self.assertEqual(project, self.mock_project)

    def test_get_tasks(self):
        """Test getting tasks"""
        client = Clockify(self.api_key)
        tasks = client.tasks.get_all(project_id=self.project_id)
        self.assertEqual(tasks, [self.mock_task])

    def test_get_time_entries(self):
        """Test getting time entries"""
        client = Clockify(self.api_key)
        time_entries = client.time_entries.get_by_user_id(user_id=self.user_id)
        self.assertEqual(time_entries, [self.mock_time_entry])

    def test_start_timer(self):
        """Test starting a timer"""
        client = Clockify(self.api_key)
        client.time_entries.workspace_id = self.workspace_id

        # Use datetime objects instead of strings

        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=1)

        time_entry = client.time_entries.create(
            start=start_time,
            end=end_time,
            description="Test Time Entry",
            project_id=self.project_id,
            task_id=self.task_id,
        )
        self.assertEqual(time_entry, self.mock_running_time_entry)

    def test_stop_timer(self):
        """Test stopping a timer"""
        client = Clockify(self.api_key)
        client.time_entries.workspace_id = self.workspace_id

        # Mock a running time entry
        self.mock_session.request.side_effect = None
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = [self.mock_running_time_entry]
        self.mock_session.request.return_value = mock_response

        # First get the running time entry
        time_entries = client.time_entries.get_by_user_id(user_id=self.user_id)
        running_entry = next(
            (
                entry
                for entry in time_entries
                if entry.get("timeInterval", {}).get("end") is None
            ),
            None,
        )
        self.assertIsNotNone(running_entry)

        # Reset mock for update call
        mock_response.json.return_value = self.mock_time_entry

        end_time = datetime.now()

        # Then stop it
        time_entry = client.time_entries.update(
            running_entry["id"],
            end=end_time,
        )
        self.assertEqual(time_entry, self.mock_time_entry)
