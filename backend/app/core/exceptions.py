from fastapi import status


class RAGException(Exception):
    """Base exception for all RAG-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(RAGException):
    """Exception for database-related errors."""

    def __init__(self, message: str = "Database operation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class VectorStoreException(RAGException):
    """Exception for vector store operations."""

    def __init__(self, message: str = "Vector store operation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ValidationException(RAGException):
    """Exception for validation errors."""

    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class NotFoundException(RAGException):
    """Exception for resource not found errors."""

    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class LLMException(RAGException):
    """Exception for LLM/AI model errors."""

    def __init__(self, message: str = "LLM operation failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class AuthenticationException(RAGException):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )
