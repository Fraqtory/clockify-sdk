"""Test cases for the Clockify SDK"""

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

        # Create patcher for httpx
        self.httpx_patcher = mock.patch("clockify_sdk.connection.httpx")
        self.mock_httpx = self.httpx_patcher.start()

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
            return mock.Mock(status_code=404)

        # Configure the mock client to use our mock request function
        mock_client = mock.Mock()
        mock_client.request.side_effect = mock_request
        self.mock_httpx.Client.return_value = mock_client

        # Initialize the client
        self.client = Clockify(api_key=self.api_key)

    def tearDown(self):
        """Clean up test fixtures"""
        self.httpx_patcher.stop()

    def test_init(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.user_id, self.user_id)
        self.assertEqual(self.client.workspace_id, self.workspace_id)

    def test_get_workspaces(self):
        """Test getting workspaces"""
        workspaces = self.client.get_workspaces()
        self.assertEqual(workspaces, self.mock_workspaces)

    def test_get_projects(self):
        """Test getting projects"""
        mock_projects_response = mock.Mock()
        mock_projects_response.status_code = 200
        mock_projects_response.json.return_value = [self.mock_project]

        def mock_request(**kwargs):
            if kwargs["url"].endswith("/projects"):
                return mock_projects_response
            return mock.Mock(status_code=404)

        self.mock_httpx.Client.return_value.request.side_effect = mock_request

        projects = self.client.get_projects()
        self.assertEqual(projects, [self.mock_project])

    def test_get_project(self):
        """Test getting a project"""
        mock_project_response = mock.Mock()
        mock_project_response.status_code = 200
        mock_project_response.json.return_value = self.mock_project

        def mock_request(**kwargs):
            if kwargs["url"].endswith(self.project_id):
                return mock_project_response
            return mock.Mock(status_code=404)

        self.mock_httpx.Client.return_value.request.side_effect = mock_request

        project = self.client.get_project(self.project_id)
        self.assertEqual(project, self.mock_project)

    def test_get_tasks(self):
        """Test getting tasks"""
        mock_tasks_response = mock.Mock()
        mock_tasks_response.status_code = 200
        mock_tasks_response.json.return_value = [self.mock_task]

        def mock_request(**kwargs):
            if kwargs["url"].endswith("/tasks"):
                return mock_tasks_response
            return mock.Mock(status_code=404)

        self.mock_httpx.Client.return_value.request.side_effect = mock_request

        tasks = self.client.get_tasks(self.project_id)
        self.assertEqual(tasks, [self.mock_task])

    def test_get_time_entries(self):
        """Test getting time entries"""
        mock_time_entries_response = mock.Mock()
        mock_time_entries_response.status_code = 200
        mock_time_entries_response.json.return_value = [self.mock_time_entry]

        def mock_request(**kwargs):
            if kwargs["url"].endswith("/time-entries"):
                return mock_time_entries_response
            return mock.Mock(status_code=404)

        self.mock_httpx.Client.return_value.request.side_effect = mock_request

        time_entries = self.client.get_time_entries()
        self.assertEqual(time_entries, [self.mock_time_entry])

    def test_start_timer(self):
        """Test starting a timer"""
        mock_start_timer_response = mock.Mock()
        mock_start_timer_response.status_code = 201
        mock_start_timer_response.json.return_value = self.mock_time_entry

        def mock_request(**kwargs):
            if kwargs["method"] == "POST" and kwargs["url"].endswith("/time-entries"):
                return mock_start_timer_response
            return mock.Mock(status_code=404)

        self.mock_httpx.Client.return_value.request.side_effect = mock_request

        # Set workspace_id in the time entries manager
        self.client.time_entries.workspace_id = self.workspace_id

        time_entry = self.client.start_timer(
            description="Test Time Entry",
            project_id=self.project_id,
            task_id=self.task_id,
        )
        self.assertEqual(time_entry, self.mock_time_entry)

    def test_stop_timer(self):
        """Test stopping a timer"""
        # Mock get_all response to return a running time entry
        mock_get_entries_response = mock.Mock()
        mock_get_entries_response.status_code = 200
        mock_get_entries_response.json.return_value = [self.mock_running_time_entry]

        # Mock update response
        mock_update_response = mock.Mock()
        mock_update_response.status_code = 200
        mock_update_response.json.return_value = self.mock_time_entry

        def mock_request(**kwargs):
            if kwargs["method"] == "GET" and kwargs["url"].endswith("/time-entries"):
                return mock_get_entries_response
            elif kwargs["method"] == "PUT" and kwargs["url"].endswith(
                self.time_entry_id
            ):
                return mock_update_response
            return mock.Mock(status_code=404)

        self.mock_httpx.Client.return_value.request.side_effect = mock_request

        # Set workspace_id in the time entries manager
        self.client.time_entries.workspace_id = self.workspace_id

        time_entry = self.client.stop_timer()
        self.assertEqual(time_entry, self.mock_time_entry)
