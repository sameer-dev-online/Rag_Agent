from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""

    document_id: str
    title: str
    file_name: str
    file_type: str
    num_chunks: int
    content_length: int

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "880e8400-e29b-41d4-a716-446655440000",
                "title": "Company Handbook 2024",
                "file_name": "handbook.pdf",
                "file_type": "pdf",
                "num_chunks": 45,
                "content_length": 12500
            }
        }


class DocumentSchema(BaseModel):
    """Schema for a document."""

    id: str
    user_id: str
    title: str
    file_name: str
    file_type: str
    source_type: str
    source_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "user_id": "user123",
                "title": "Company Handbook 2024",
                "file_name": "handbook.pdf",
                "file_type": "pdf",
                "source_type": "upload",
                "source_metadata": {"content_length": 12500},
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }
