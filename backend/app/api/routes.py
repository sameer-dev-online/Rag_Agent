from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional

from app.api.dependencies import verify_api_key
from app.services.rag_service import RAGService
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import DocumentUploadResponse
from app.schemas.response import success_response, error_response
from app.core.exceptions import RAGException, NotFoundException, ValidationException


# Create API router
router = APIRouter()


# Initialize RAG service (singleton pattern)
rag_service = RAGService()


@router.get("/health")
async def health_check():
    """
    Health check endpoint (no authentication required).

    Returns:
        Success response with health status
    """
    return success_response(
        data={"status": "healthy"},
        message="Service is running",
        status=200
    )


@router.post("/chat", dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    """
    Process a chat message through the RAG pipeline.

    Requires:
        - X-API-Key header for authentication

    Args:
        request: ChatRequest with message, user_id, and optional conversation_id

    Returns:
        APIResponse with conversation_id, user_message, assistant_message, and contexts
    """
    try:
        result = await rag_service.process_query(
            user_id=request.user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )

        return success_response(
            data=result,
            message="Message processed successfully",
            status=200
        )

    except NotFoundException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except ValidationException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except RAGException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except Exception as e:
        return error_response(
            message="An unexpected error occurred",
            status=500,
            data={"error": str(e)}
        )


@router.post("/documents", dependencies=[Depends(verify_api_key)])
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    title: Optional[str] = Form(None)
):
    """
    Upload a document to the knowledge base.

    Requires:
        - X-API-Key header for authentication
        - Content-Type: multipart/form-data

    Args:
        file: PDF, TXT, or DOCX file
        user_id: User identifier
        title: Optional document title (defaults to filename)

    Returns:
        APIResponse with document_id, title, and num_chunks
    """
    try:
        result = await rag_service.add_document(
            user_id=user_id,
            file=file,
            title=title
        )

        return success_response(
            data=result,
            message="Document uploaded successfully",
            status=201
        )

    except ValidationException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except RAGException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except Exception as e:
        return error_response(
            message="An unexpected error occurred",
            status=500,
            data={"error": str(e)}
        )


@router.get("/conversations/{conversation_id}", dependencies=[Depends(verify_api_key)])
async def get_conversation(conversation_id: str, user_id: str):
    """
    Get a conversation with all messages.

    Requires:
        - X-API-Key header for authentication

    Args:
        conversation_id: Conversation UUID
        user_id: User identifier (query parameter)

    Returns:
        APIResponse with conversation and messages
    """
    try:
        result = rag_service.get_conversation_with_messages(
            conversation_id=conversation_id,
            user_id=user_id
        )

        return success_response(
            data=result,
            message="Conversation retrieved successfully",
            status=200
        )

    except NotFoundException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except RAGException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except Exception as e:
        return error_response(
            message="An unexpected error occurred",
            status=500,
            data={"error": str(e)}
        )


@router.delete("/documents/{document_id}", dependencies=[Depends(verify_api_key)])
async def delete_document(document_id: str, user_id: Optional[str] = None):
    """
    Delete a document and its embeddings.

    Requires:
        - X-API-Key header for authentication

    Args:
        document_id: Document UUID
        user_id: Optional user identifier (query parameter)

    Returns:
        APIResponse with success message
    """
    try:
        rag_service.delete_document(
            document_id=document_id,
            user_id=user_id
        )

        return success_response(
            data=None,
            message="Document deleted successfully",
            status=200
        )

    except NotFoundException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except RAGException as e:
        return error_response(
            message=e.message,
            status=e.status_code,
            data=e.details
        )
    except Exception as e:
        return error_response(
            message="An unexpected error occurred",
            status=500,
            data={"error": str(e)}
        )
