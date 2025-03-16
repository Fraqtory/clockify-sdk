"""
Client model and manager for Clockify API
"""
from typing import Dict, List, Optional

from ..base.client import ClockifyBaseClient


class ClientManager(ClockifyBaseClient):
    """Manager for Clockify client operations"""

    def __init__(self, api_key: str, workspace_id: str):
        """
        Initialize the client manager

        Args:
            api_key: Clockify API key
            workspace_id: Workspace ID
        """
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_clients(self) -> List[Dict]:
        """
        Get all clients in the workspace

        Returns:
            List of client objects
        """
        return self._request("GET", f"workspaces/{self.workspace_id}/clients")

    def get_client(self, client_id: str) -> Dict:
        """
        Get a specific client by ID

        Args:
            client_id: Client ID

        Returns:
            Client object
        """
        return self._request("GET", f"workspaces/{self.workspace_id}/clients/{client_id}")

    def create_client(self, name: str, address: Optional[str] = None) -> Dict:
        """
        Create a new client

        Args:
            name: Client name
            address: Optional client address

        Returns:
            Created client object
        """
        data = {
            "name": name,
            "address": address
        }
        return self._request(
            "POST", 
            f"workspaces/{self.workspace_id}/clients",
            data={k: v for k, v in data.items() if v is not None}
        )

    def update_client(self, client_id: str, name: str, address: Optional[str] = None) -> Dict:
        """
        Update an existing client

        Args:
            client_id: Client ID
            name: New client name
            address: Optional new client address

        Returns:
            Updated client object
        """
        data = {
            "name": name,
            "address": address
        }
        return self._request(
            "PUT",
            f"workspaces/{self.workspace_id}/clients/{client_id}",
            data={k: v for k, v in data.items() if v is not None}
        )

    def delete_client(self, client_id: str) -> None:
        """
        Delete a client

        Args:
            client_id: Client ID to delete
        """
        self._request("DELETE", f"workspaces/{self.workspace_id}/clients/{client_id}") 