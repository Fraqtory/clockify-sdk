from typing import Dict, List, Optional
from ..base.client import ClockifyClient

class ClientManager(ClockifyClient):
    """Handles client operations in Clockify"""

    def __init__(self, api_key: str, workspace_id: str):
        super().__init__(api_key)
        self.workspace_id = workspace_id

    def get_clients(self) -> List[Dict]:
        """
        Get all clients in the workspace

        Returns:
            List of clients
        """
        endpoint = f"workspaces/{self.workspace_id}/clients"
        return self._request("GET", endpoint)

    def get_client(self, client_id: str) -> Dict:
        """
        Get a specific client by ID

        Args:
            client_id: ID of the client to retrieve

        Returns:
            Client data
        """
        endpoint = f"workspaces/{self.workspace_id}/clients/{client_id}"
        return self._request("GET", endpoint)

    def create_client(self, name: str, address: Optional[str] = None, 
                     note: Optional[str] = None) -> Dict:
        """
        Create a new client

        Args:
            name: Name of the client
            address: Optional address of the client
            note: Optional note about the client

        Returns:
            Created client data
        """
        data = {
            "name": name,
        }
        if address:
            data["address"] = address
        if note:
            data["note"] = note

        endpoint = f"workspaces/{self.workspace_id}/clients"
        return self._request("POST", endpoint, data=data)

    def update_client(self, client_id: str, name: Optional[str] = None,
                     address: Optional[str] = None, note: Optional[str] = None) -> Dict:
        """
        Update an existing client

        Args:
            client_id: ID of the client to update
            name: Optional new name for the client
            address: Optional new address for the client
            note: Optional new note for the client

        Returns:
            Updated client data
        """
        data = {}
        if name:
            data["name"] = name
        if address:
            data["address"] = address
        if note:
            data["note"] = note

        endpoint = f"workspaces/{self.workspace_id}/clients/{client_id}"
        return self._request("PUT", endpoint, data=data)

    def delete_client(self, client_id: str) -> None:
        """
        Delete a client

        Args:
            client_id: ID of the client to delete
        """
        endpoint = f"workspaces/{self.workspace_id}/clients/{client_id}"
        self._request("DELETE", endpoint) 