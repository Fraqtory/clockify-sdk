"""
Client model and manager for Clockify API
"""

from typing import Any, Dict, List, Optional

from ..base.client import ClockifyBaseClient


class ClientManager(ClockifyBaseClient):
    """Manager for Clockify client operations"""

    def __init__(self, api_key: str, workspace_id: str) -> None:
        """
        Initialize the client manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_clients(self) -> List[Dict[str, Any]]:
        """
        Get all clients in the workspace

        Returns:
            List of client objects
        """
        return self._request("GET", f"workspaces/{self.workspace_id}/clients")

    def get_client(self, client_id: str) -> Dict[str, Any]:
        """
        Get a specific client by ID

        Args:
            client_id: Client ID

        Returns:
            Client object
        """
        return self._request(
            "GET", f"workspaces/{self.workspace_id}/clients/{client_id}"
        )

    def create_client(
        self,
        name: str,
        email: Optional[str] = None,
        note: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create a new client

        Args:
            name: Client name
            email: Optional client email
            note: Optional client note
            archived: Optional archived flag

        Returns:
            Created client object
        """
        data: Dict[str, Any] = {"name": name}
        if email:
            data["email"] = email
        if note:
            data["note"] = note
        if archived is not None:
            data["archived"] = archived

        return self._request(
            "POST", f"workspaces/{self.workspace_id}/clients", data=data
        )

    def update_client(
        self,
        client_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        note: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing client

        Args:
            client_id: Client ID
            name: New client name
            email: Optional new client email
            note: Optional client note
            archived: Optional archived flag

        Returns:
            Updated client object
        """
        data: Dict[str, Any] = {}
        if name:
            data["name"] = name
        if email:
            data["email"] = email
        if note:
            data["note"] = note
        if archived is not None:
            data["archived"] = archived

        return self._request(
            "PUT", f"workspaces/{self.workspace_id}/clients/{client_id}", data=data
        )

    def delete_client(self, client_id: str) -> Dict[str, Any]:
        """
        Delete a client

        Args:
            client_id: Client ID to delete

        Returns:
            Deleted client
        """
        return self._request(
            "DELETE", f"workspaces/{self.workspace_id}/clients/{client_id}"
        )
