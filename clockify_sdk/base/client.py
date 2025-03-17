"""
Base client for the Clockify SDK
"""

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from ..config import Config
from ..connection import ConnectionManager
from ..logging import logger

SingleResponse = TypeVar("SingleResponse", bound=Dict[str, Any])
ListResponse = TypeVar("ListResponse", bound=List[Dict[str, Any]])


class ApiClientBase(Generic[SingleResponse, ListResponse]):
    """Base class for making requests to the Clockify API.
    Provides common functionality for API clients."""

    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the base client.

        Args:
            connection_manager: Connection manager for making HTTP requests
        """
        self._connection = connection_manager

    @overload
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_type: Type[SingleResponse],
    ) -> SingleResponse: ...

    @overload
    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_type: Type[ListResponse],
    ) -> ListResponse: ...

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_type: Union[Type[SingleResponse], Type[ListResponse]],
    ) -> Union[SingleResponse, ListResponse]:
        """Make a request to the Clockify API.

        Args:
            method: HTTP method
            path: API path
            json: Request body
            params: Query parameters
            response_type: Expected response type

        Returns:
            API response

        Raises:
            ClockifyError: If the API request fails
        """
        url = f"{Config.BASE_URL}/{path}"
        try:
            response = self._connection.request(
                method=method, url=url, json=json, params=params
            )
            if response_type == List[Dict[str, Any]]:
                return cast("ListResponse", response)
            return cast("SingleResponse", response)
        except Exception as e:
            logger.error(f"API request failed: {e!s}")
            raise

    def close(self) -> None:
        """Close the session"""
        self._connection.close()
