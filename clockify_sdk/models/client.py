"""
Client model for the Clockify SDK
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from ..base.client import ApiClientBase
from .base import ClockifyBaseModel


class Client(ClockifyBaseModel):
    """Client model representing a Clockify client."""

    id: str = Field(..., description="Client ID")
    name: str = Field(..., description="Client name")
    workspace_id: str = Field(..., description="Workspace ID")
    note: Optional[str] = Field(None, description="Client note")
    address: Optional[str] = Field(None, description="Client address")
    email: Optional[str] = Field(None, description="Client email")
    phone: Optional[str] = Field(None, description="Client phone")
    website: Optional[str] = Field(None, description="Client website")
    is_archived: bool = Field(False, description="Whether the client is archived")
    custom_fields: List[Dict[str, Any]] = Field(
        default_factory=list, description="Custom fields"
    )


class ClientManager(ApiClientBase[Dict[str, Any], List[Dict[str, Any]]]):
    """Manager for client-related operations."""

    def get_all(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all clients in a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of clients
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/clients",
            response_type=List[Dict[str, Any]],
        )

    def get_by_id(self, workspace_id: str, client_id: str) -> Dict[str, Any]:
        """Get a specific client by ID.

        Args:
            workspace_id: ID of the workspace
            client_id: ID of the client

        Returns:
            Client information
        """
        return self._request(
            "GET",
            f"workspaces/{workspace_id}/clients/{client_id}",
            response_type=Dict[str, Any],
        )

    def create(self, workspace_id: str, client: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client.

        Args:
            workspace_id: ID of the workspace
            client: Client data

        Returns:
            Created client information
        """
        return self._request(
            "POST",
            f"workspaces/{workspace_id}/clients",
            json=client,
            response_type=Dict[str, Any],
        )

    def update(
        self, workspace_id: str, client_id: str, client: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing client.

        Args:
            workspace_id: ID of the workspace
            client_id: ID of the client
            client: Updated client data

        Returns:
            Updated client information
        """
        return self._request(
            "PUT",
            f"workspaces/{workspace_id}/clients/{client_id}",
            json=client,
            response_type=Dict[str, Any],
        )

    def delete(self, workspace_id: str, client_id: str) -> None:
        """Delete a client.

        Args:
            workspace_id: ID of the workspace
            client_id: ID of the client
        """
        self._request(
            "DELETE",
            f"workspaces/{workspace_id}/clients/{client_id}",
            response_type=Dict[str, Any],
        )
