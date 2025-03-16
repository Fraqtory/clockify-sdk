"""Tests for the Clockify SDK."""

from unittest import TestCase
from unittest import mock

from clockify_sdk import ClockifyClient


class TestClockifyClient(TestCase):
    """Test cases for ClockifyClient"""

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

        # Create patcher for requests
        self.requests_patcher = mock.patch("clockify_sdk.base.client.requests")
        self.mock_requests = self.requests_patcher.start()

        # Set up mock responses for initialization
        mock_user_response = mock.Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = self.mock_user

        mock_workspaces_response = mock.Mock()
        mock_workspaces_response.status_code = 200
        mock_workspaces_response.json.return_value = self.mock_workspaces

        # Configure request mock to return different responses
        def mock_request(**kwargs):
            if kwargs["url"].endswith("/user"):
                return mock_user_response
            elif kwargs["url"].endswith("/workspaces"):
                return mock_workspaces_response
            elif kwargs["url"].endswith("/projects"):
                mock_response = mock.Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = [self.mock_project]
                return mock_response
            elif kwargs["url"].endswith(f"/projects/{self.project_id}"):
                mock_response = mock.Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = self.mock_project
                return mock_response
            elif kwargs["url"].endswith("/tasks"):
                mock_response = mock.Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = [self.mock_task]
                return mock_response
            elif kwargs["url"].endswith("/time-entries"):
                mock_response = mock.Mock()
                mock_response.status_code = 200
                if kwargs["method"] == "GET":
                    mock_response.json.return_value = [self.mock_time_entry]
                else:
                    mock_response.json.return_value = self.mock_time_entry
                return mock_response
            return mock.Mock(status_code=404)

        self.mock_requests.request.side_effect = mock_request

        # Initialize client
        self.client = ClockifyClient(api_key=self.api_key)

    def tearDown(self):
        """Clean up after tests"""
        self.requests_patcher.stop()

    def test_init(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.workspace_id, self.workspace_id)
        self.assertEqual(self.client.user_manager.user_id, self.user_id)

    def test_get_workspaces(self):
        """Test getting workspaces"""
        # Make request
        workspaces = self.client.get_workspaces()

        # Verify response
        self.assertEqual(workspaces, self.mock_workspaces)
        self.assertEqual(len(workspaces), 1)
        self.assertEqual(workspaces[0]["id"], self.workspace_id)
        self.assertEqual(workspaces[0]["name"], "Test Workspace")

        # Verify request
        self.mock_requests.request.assert_any_call(
            method="GET",
            url="https://api.clockify.me/api/v1/workspaces",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json=None,
        )

    def test_get_projects(self):
        """Test getting projects"""
        # Make request
        projects = self.client.projects.get_projects()

        # Verify response
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["id"], self.project_id)
        self.assertEqual(projects[0]["name"], "Test Project")

        # Verify request
        self.mock_requests.request.assert_any_call(
            method="GET",
            url=f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/projects",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json=None,
        )

    def test_get_project(self):
        """Test getting a specific project"""
        # Make request
        project = self.client.projects.get_project(self.project_id)

        # Verify response
        self.assertEqual(project["id"], self.project_id)
        self.assertEqual(project["name"], "Test Project")

        # Verify request
        self.mock_requests.request.assert_any_call(
            method="GET",
            url=f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/projects/{self.project_id}",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json=None,
        )

    def test_get_tasks(self):
        """Test getting tasks for a project"""
        # Make request
        tasks = self.client.tasks.get_tasks(self.project_id)

        # Verify response
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], self.task_id)
        self.assertEqual(tasks[0]["name"], "Test Task")

        # Verify request
        self.mock_requests.request.assert_any_call(
            method="GET",
            url=f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/projects/{self.project_id}/tasks",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json=None,
        )

    def test_get_time_entries(self):
        """Test getting time entries"""
        # Make request
        time_entries = self.client.time_entries.get_time_entries()

        # Verify response
        self.assertEqual(len(time_entries), 1)
        self.assertEqual(time_entries[0]["id"], self.time_entry_id)
        self.assertEqual(time_entries[0]["description"], "Test Time Entry")

        # Verify request
        self.mock_requests.request.assert_any_call(
            method="GET",
            url=f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/user/{self.user_id}/time-entries",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json=None,
        )

    def test_start_timer(self):
        """Test starting a timer"""
        description = "Test Timer"

        # Make request
        time_entry = self.client.time_entries.start_timer(
            description=description, project_id=self.project_id, task_id=self.task_id
        )

        # Verify response
        self.assertEqual(time_entry["id"], self.time_entry_id)
        self.assertEqual(time_entry["description"], "Test Time Entry")

        # Verify request was made with correct data
        self.mock_requests.request.assert_any_call(
            method="POST",
            url=f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/time-entries",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json={
                "start": mock.ANY,  # We can't predict the exact time
                "description": description,
                "projectId": self.project_id,
                "taskId": self.task_id,
            },
        )

    def test_stop_timer(self):
        """Test stopping a timer"""
        # Make request
        time_entry = self.client.time_entries.stop_timer()

        # Verify response
        self.assertEqual(time_entry["id"], self.time_entry_id)
        self.assertTrue("end" in time_entry["timeInterval"])

        # Verify request
        self.mock_requests.request.assert_any_call(
            method="PATCH",
            url=f"https://api.clockify.me/api/v1/workspaces/{self.workspace_id}/user/{self.user_id}/time-entries",
            headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
            params=None,
            json={"end": mock.ANY},  # We can't predict the exact time
        )
