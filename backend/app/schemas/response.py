from typing import Generic, TypeVar, Any, Optional
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response format for all endpoints.

    Attributes:
        success: Boolean indicating if the request was successful
        message: Human-readable message describing the response
        status: HTTP status code
        data: Response data (generic type)
    """

    success: bool
    message: str
    status: int
    data: Optional[T] = None


def success_response(
    data: Any = None,
    message: str = "Operation successful",
    status: int = 200
) -> dict:
    """
    Helper function to create a successful response.

    Args:
        data: Response data
        message: Success message
        status: HTTP status code

    Returns:
        Dictionary in APIResponse format
    """
    return {
        "success": True,
        "message": message,
        "status": status,
        "data": data
    }


def error_response(
    message: str,
    status: int = 500,
    data: Any = None
) -> dict:
    """
    Helper function to create an error response.

    Args:
        message: Error message
        status: HTTP status code
        data: Additional error data

    Returns:
        Dictionary in APIResponse format
    """
    return {
        "success": False,
        "message": message,
        "status": status,
        "data": data
    }
