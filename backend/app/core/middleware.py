import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.exceptions import RAGException
from app.schemas.response import error_response


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses.
    """

    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.2f}s"
        )

        return response


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global exception handling.
    Catches all unhandled exceptions and returns standardized error responses.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RAGException as e:
            # Handle custom RAG exceptions
            logger.error(
                f"RAG Exception: {e.message} | "
                f"Status: {e.status_code} | "
                f"Details: {e.details}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=error_response(
                    message=e.message,
                    status=e.status_code,
                    data=e.details
                )
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.exception(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content=error_response(
                    message="An unexpected error occurred",
                    status=500,
                    data={"error": str(e)}
                )
            )
