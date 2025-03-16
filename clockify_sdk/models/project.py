"""Project management for Clockify API."""

from typing import Any, Dict, List, Optional

from clockify_sdk.base.client import ClockifyBaseClient, JsonDict, JsonList


class ProjectManager(ClockifyBaseClient):
    """Manager for Clockify project operations"""

    def __init__(self, api_key: str, workspace_id: str) -> None:
        """
        Initialize the project manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_projects(self) -> JsonList:
        """
        Get all projects in the workspace

        Returns:
            List of project objects
        """
        endpoint = f"workspaces/{self.workspace_id}/projects"
        return self._request("GET", endpoint, response_type=JsonList)

    def get_project(self, project_id: str) -> JsonDict:
        """
        Get a specific project by ID

        Args:
            project_id: Project ID

        Returns:
            Project object
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}"
        return self._request("GET", endpoint, response_type=JsonDict)

    def create_project(
        self,
        name: str,
        client_id: Optional[str] = None,
        color: Optional[str] = None,
        note: Optional[str] = None,
        billable: Optional[bool] = None,
        public: Optional[bool] = None,
    ) -> JsonDict:
        """
        Create a new project

        Args:
            name: Project name
            client_id: Optional client ID to associate with the project
            color: Optional color hex code
            note: Optional project note
            billable: Optional billable flag
            public: Optional public flag

        Returns:
            Created project object
        """
        data: Dict[str, Any] = {"name": name}
        if client_id:
            data["clientId"] = client_id
        if color:
            data["color"] = color
        if note:
            data["note"] = note
        if billable is not None:
            data["billable"] = billable
        if public is not None:
            data["public"] = public

        endpoint = f"workspaces/{self.workspace_id}/projects"
        return self._request("POST", endpoint, data=data, response_type=JsonDict)

    def get_tasks(self, project_id: str) -> JsonList:
        """
        Get all tasks for a project

        Args:
            project_id: Project ID to get tasks for

        Returns:
            List of tasks
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("GET", endpoint, response_type=JsonList)

    def create_task(
        self,
        project_id: str,
        name: str,
        assignee_ids: Optional[List[str]] = None,
    ) -> JsonDict:
        """
        Create a new task in a project

        Args:
            project_id: Project ID to create task in
            name: Task name
            assignee_ids: Optional list of user IDs to assign to the task

        Returns:
            Task data
        """
        data: Dict[str, Any] = {
            "name": name,
            "projectId": project_id,
        }
        if assignee_ids:
            data["assigneeIds"] = assignee_ids

        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}/tasks"
        return self._request("POST", endpoint, data=data, response_type=JsonDict)

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        client_id: Optional[str] = None,
        color: Optional[str] = None,
        note: Optional[str] = None,
        billable: Optional[bool] = None,
        public: Optional[bool] = None,
        archived: Optional[bool] = None,
    ) -> JsonDict:
        """Update a project.

        Args:
            project_id: Project ID
            name: Optional new project name
            client_id: Optional client ID
            color: Optional color hex code
            note: Optional project note
            billable: Optional billable flag
            public: Optional public flag
            archived: Optional archived flag

        Returns:
            Updated project
        """
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if client_id:
            data["clientId"] = client_id
        if color:
            data["color"] = color
        if note:
            data["note"] = note
        if billable is not None:
            data["billable"] = billable
        if public is not None:
            data["public"] = public
        if archived is not None:
            data["archived"] = archived

        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}"
        return self._request("PUT", endpoint, data=data, response_type=JsonDict)

    def delete_project(self, project_id: str) -> JsonDict:
        """Delete a project.

        Args:
            project_id: Project ID

        Returns:
            Deleted project
        """
        endpoint = f"workspaces/{self.workspace_id}/projects/{project_id}"
        return self._request("DELETE", endpoint, response_type=JsonDict)
