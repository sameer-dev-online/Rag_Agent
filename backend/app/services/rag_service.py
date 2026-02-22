from typing import Dict, Any, Optional, List
from fastapi import UploadFile

from app.services.vector_service import VectorService
from app.services.memory_service import MemoryService
from app.services.document_service import DocumentService
from app.core.agent import run_agent
from app.core.exceptions import RAGException


class RAGService:
    """
    Orchestrates the complete RAG pipeline.
    Coordinates between vector search, memory management, and AI agent.
    """

    def __init__(self):
        """Initialize RAGService with all required services."""
        self.vector_service = VectorService()
        self.memory_service = MemoryService()
        self.document_service = DocumentService()

    async def process_query(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.

        Pipeline Steps:
        1. Create or get conversation
        2. Retrieve relevant context from vector store
        3. Get conversation history
        4. Store user message
        5. Run AI agent with context
        6. Store assistant response
        7. Return formatted response

        Args:
            user_id: User identifier
            message: User's message/query
            conversation_id: Optional existing conversation ID

        Returns:
            Dictionary containing conversation_id, user_message, assistant_message, and contexts
        """
        try:
            # Step 1: Create or get conversation
            if conversation_id:
                # Verify conversation exists and belongs to user
                conversation = self.memory_service.get_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id
                )
            else:
                # Create new conversation
                conversation = self.memory_service.create_conversation(
                    user_id=user_id,
                    title=self._generate_title_from_message(message)
                )
                conversation_id = conversation["id"]

            # Step 2: Retrieve relevant context
            retrieved_contexts = self.vector_service.similarity_search(
                query=message,
                filter_metadata={"user_id": user_id} if user_id else None
            )

            # Step 3: Get conversation history
            conversation_history = self.memory_service.get_recent_messages(
                conversation_id=conversation_id
            )

            # Step 4: Store user message
            user_message = self.memory_service.create_message(
                conversation_id=conversation_id,
                role="user",
                content=message
            )

            # Step 5: Run AI agent
            assistant_response = await run_agent(
                query=message,
                retrieved_contexts=retrieved_contexts,
                conversation_history=conversation_history
            )

            # Step 6: Store assistant response
            assistant_message = self.memory_service.create_message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response,
                metadata={
                    "contexts_used": len(retrieved_contexts),
                    "context_ids": [ctx["id"] for ctx in retrieved_contexts]
                }
            )

            # Step 7: Update conversation title if it's a new conversation
            if not conversation_id or len(conversation_history) == 0:
                self.memory_service.update_conversation(
                    conversation_id=conversation_id,
                    title=self._generate_title_from_message(message)
                )

            # Step 8: Return formatted response
            return {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "retrieved_contexts": retrieved_contexts
            }

        except Exception as e:
            if isinstance(e, RAGException):
                raise
            raise RAGException(
                message=f"Failed to process query: {str(e)}",
                details={"error": str(e), "user_id": user_id}
            )

    async def add_document(
        self,
        user_id: str,
        file: UploadFile,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the knowledge base.

        Pipeline Steps:
        1. Parse file and extract text
        2. Store document in database
        3. Chunk text and generate embeddings
        4. Store embeddings in vector database
        5. Return document info

        Args:
            user_id: User identifier
            file: Uploaded file
            title: Optional document title (defaults to filename)

        Returns:
            Dictionary containing document_id, title, and num_chunks
        """
        try:
            # Step 1: Parse file
            content = self.document_service.parse_file(file)

            # Get file type and name
            file_type = self.document_service._get_file_type(file)
            file_name = file.filename or "untitled"
            doc_title = title or file_name

            # Step 2: Store document in database
            document = self.document_service.create_document(
                user_id=user_id,
                title=doc_title,
                content=content,
                file_name=file_name,
                file_type=file_type,
                source_type="upload",
                source_metadata={
                    "content_length": len(content),
                    "original_filename": file_name
                }
            )

            document_id = document["id"]

            # Step 3 & 4: Chunk and embed document
            num_chunks = self.vector_service.add_document_embeddings(
                document_id=document_id,
                text=content,
                metadata={
                    "user_id": user_id,
                    "title": doc_title,
                    "file_name": file_name,
                    "file_type": file_type
                }
            )

            # Step 5: Return document info
            return {
                "document_id": document_id,
                "title": doc_title,
                "file_name": file_name,
                "file_type": file_type,
                "num_chunks": num_chunks,
                "content_length": len(content)
            }

        except Exception as e:
            if isinstance(e, RAGException):
                raise
            raise RAGException(
                message=f"Failed to add document: {str(e)}",
                details={"error": str(e), "user_id": user_id}
            )

    def delete_document(self, document_id: str, user_id: Optional[str] = None) -> None:
        """
        Delete a document and its embeddings.

        Args:
            document_id: Document UUID
            user_id: Optional user ID for authorization
        """
        try:
            # Delete from vector store
            self.vector_service.delete_document_embeddings(document_id)

            # Delete from database
            self.document_service.delete_document(document_id)

        except Exception as e:
            if isinstance(e, RAGException):
                raise
            raise RAGException(
                message=f"Failed to delete document: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )

    def get_conversation_with_messages(
        self,
        conversation_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a conversation with all its messages.

        Args:
            conversation_id: Conversation UUID
            user_id: Optional user ID for authorization

        Returns:
            Dictionary containing conversation and messages
        """
        try:
            conversation = self.memory_service.get_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )

            messages = self.memory_service.get_conversation_messages(
                conversation_id=conversation_id
            )

            return {
                "conversation": conversation,
                "messages": messages
            }

        except Exception as e:
            if isinstance(e, RAGException):
                raise
            raise RAGException(
                message=f"Failed to get conversation: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    def _generate_title_from_message(self, message: str, max_length: int = 50) -> str:
        """
        Generate a conversation title from the first message.

        Args:
            message: User's message
            max_length: Maximum title length

        Returns:
            Generated title
        """
        # Take first line or sentence
        title = message.split("\n")[0].strip()

        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."

        return title if title else "New Conversation"
