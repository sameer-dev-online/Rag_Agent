from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from supabase import create_client, Client

from app.config import settings
from app.core.exceptions import DatabaseException, NotFoundException


class MemoryService:
    """
    Service for managing conversations and messages in Supabase.
    Handles all database CRUD operations for conversation history.
    """

    def __init__(self):
        """Initialize MemoryService with Supabase client."""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to initialize MemoryService: {str(e)}",
                details={"error": str(e)}
            )

    # ===== Conversation Operations =====

    def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.

        Args:
            user_id: User identifier
            title: Optional conversation title
            metadata: Optional metadata dictionary

        Returns:
            Created conversation record
        """
        try:
            data = {
                "user_id": user_id,
                "title": title or f"Conversation at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "metadata": metadata or {}
            }

            response = self.client.table("conversations").insert(data).execute()

            if not response.data:
                raise DatabaseException("Failed to create conversation")

            return response.data[0]

        except Exception as e:
            if isinstance(e, DatabaseException):
                raise
            raise DatabaseException(
                message=f"Failed to create conversation: {str(e)}",
                details={"error": str(e), "user_id": user_id}
            )

    def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation UUID
            user_id: Optional user ID for authorization check

        Returns:
            Conversation record

        Raises:
            NotFoundException: If conversation not found
        """
        try:
            query = self.client.table("conversations").select("*").eq("id", conversation_id)

            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()

            if not response.data:
                raise NotFoundException(
                    message="Conversation not found",
                    details={"conversation_id": conversation_id}
                )

            return response.data[0]

        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to get conversation: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversation records
        """
        try:
            response = (
                self.client.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return response.data or []

        except Exception as e:
            raise DatabaseException(
                message=f"Failed to get user conversations: {str(e)}",
                details={"error": str(e), "user_id": user_id}
            )

    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a conversation.

        Args:
            conversation_id: Conversation UUID
            title: New title
            metadata: New metadata

        Returns:
            Updated conversation record
        """
        try:
            data = {}
            if title is not None:
                data["title"] = title
            if metadata is not None:
                data["metadata"] = metadata

            response = (
                self.client.table("conversations")
                .update(data)
                .eq("id", conversation_id)
                .execute()
            )

            if not response.data:
                raise NotFoundException(
                    message="Conversation not found",
                    details={"conversation_id": conversation_id}
                )

            return response.data[0]

        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to update conversation: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation and all its messages (cascade).

        Args:
            conversation_id: Conversation UUID
        """
        try:
            response = (
                self.client.table("conversations")
                .delete()
                .eq("id", conversation_id)
                .execute()
            )

            if not response.data:
                raise NotFoundException(
                    message="Conversation not found",
                    details={"conversation_id": conversation_id}
                )

        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to delete conversation: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    # ===== Message Operations =====

    def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new message in a conversation.

        Args:
            conversation_id: Conversation UUID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            Created message record
        """
        try:
            data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }

            response = self.client.table("messages").insert(data).execute()

            if not response.data:
                raise DatabaseException("Failed to create message")

            return response.data[0]

        except Exception as e:
            if isinstance(e, DatabaseException):
                raise
            raise DatabaseException(
                message=f"Failed to create message: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation, ordered by creation time.

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return (None for all)
            offset: Number of messages to skip

        Returns:
            List of message records
        """
        try:
            query = (
                self.client.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=False)
            )

            if limit is not None:
                query = query.range(offset, offset + limit - 1)

            response = query.execute()

            return response.data or []

        except Exception as e:
            raise DatabaseException(
                message=f"Failed to get conversation messages: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from a conversation.

        Args:
            conversation_id: Conversation UUID
            limit: Number of recent messages (defaults to settings.max_memory_messages)

        Returns:
            List of recent message records
        """
        try:
            if limit is None:
                limit = settings.max_memory_messages

            response = (
                self.client.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            # Reverse to get chronological order
            messages = response.data or []
            return list(reversed(messages))

        except Exception as e:
            raise DatabaseException(
                message=f"Failed to get recent messages: {str(e)}",
                details={"error": str(e), "conversation_id": conversation_id}
            )

    def delete_message(self, message_id: str) -> None:
        """
        Delete a specific message.

        Args:
            message_id: Message UUID
        """
        try:
            response = (
                self.client.table("messages")
                .delete()
                .eq("id", message_id)
                .execute()
            )

            if not response.data:
                raise NotFoundException(
                    message="Message not found",
                    details={"message_id": message_id}
                )

        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to delete message: {str(e)}",
                details={"error": str(e), "message_id": message_id}
            )

    # ===== Utility Methods =====

    def conversation_exists(self, conversation_id: str) -> bool:
        """
        Check if a conversation exists.

        Args:
            conversation_id: Conversation UUID

        Returns:
            True if conversation exists, False otherwise
        """
        try:
            response = (
                self.client.table("conversations")
                .select("id")
                .eq("id", conversation_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception:
            return False
