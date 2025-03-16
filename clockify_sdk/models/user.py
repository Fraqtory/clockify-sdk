from typing import Dict, List
from ..base.client import ClockifyClient

class UserManager(ClockifyClient):
    """Handles user-related operations in Clockify"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.user_id = None
        self.workspace_id = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize connection and retrieve basic user info"""
        user_info = self.get_current_user()
        self.user_id = user_info.get("id")
        
        workspaces = self.get_workspaces()
        if workspaces:
            self.workspace_id = workspaces[0].get("id")  # Default to first workspace

    def get_current_user(self) -> Dict:
        """Get current user data"""
        return self._request("GET", "user")

    def get_workspaces(self) -> List[Dict]:
        """Get all workspaces"""
        return self._request("GET", "workspaces")

    def set_active_workspace(self, workspace_id: str) -> None:
        """Set the active workspace for subsequent operations"""
        self.workspace_id = workspace_id 