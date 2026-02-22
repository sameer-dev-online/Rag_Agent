from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(..., min_length=1, description="User's message")
    user_id: str = Field(..., min_length=1, description="User identifier")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue existing conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the company policy on remote work?",
                "user_id": "user123",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class MessageSchema(BaseModel):
    """Schema for a message."""

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
    metadata: Dict[str, Any] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "What is the company policy?",
                "created_at": "2024-01-15T10:30:00Z",
                "metadata": {}
            }
        }


class RetrievedContext(BaseModel):
    """Schema for retrieved context chunk."""

    id: str
    similarity_score: float
    chunk_text: str
    document_id: str
    chunk_index: int
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: str
    user_message: MessageSchema
    assistant_message: MessageSchema
    retrieved_contexts: List[RetrievedContext]

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_message": {
                    "id": "660e8400-e29b-41d4-a716-446655440000",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "user",
                    "content": "What is the company policy?",
                    "created_at": "2024-01-15T10:30:00Z",
                    "metadata": {}
                },
                "assistant_message": {
                    "id": "770e8400-e29b-41d4-a716-446655440000",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "assistant",
                    "content": "According to the company policy...",
                    "created_at": "2024-01-15T10:30:05Z",
                    "metadata": {"contexts_used": 2}
                },
                "retrieved_contexts": []
            }
        }


class ConversationSchema(BaseModel):
    """Schema for a conversation."""

    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}


class ConversationWithMessages(BaseModel):
    """Schema for conversation with messages."""

    conversation: ConversationSchema
    messages: List[MessageSchema]
