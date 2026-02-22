from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import router
from app.core.middleware import LoggingMiddleware, ExceptionHandlingMiddleware
from app.core.exceptions import RAGException
from app.schemas.response import error_response


# Create FastAPI application
app = FastAPI(
    title="RAG Backend API",
    description="Production-ready RAG backend using FastAPI, PydanticAI, LangChain, and Supabase",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add custom middleware
app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(LoggingMiddleware)


# Include API routes
app.include_router(router, prefix=settings.api_v1_prefix)


# Global exception handler for RAGException
@app.exception_handler(RAGException)
async def rag_exception_handler(request, exc: RAGException):
    """
    Global exception handler for RAG exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            status=exc.status_code,
            data=exc.details
        )
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "RAG Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": f"{settings.api_v1_prefix}/docs" if settings.is_development else "disabled",
        "health": f"{settings.api_v1_prefix}/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    print("=" * 60)
    print("RAG Backend API Starting...")
    print(f"Environment: {settings.environment}")
    print(f"API Prefix: {settings.api_v1_prefix}")
    print(f"Log Level: {settings.log_level}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Embedding Model: {settings.embedding_model}")
    print("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    print("=" * 60)
    print("RAG Backend API Shutting Down...")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
