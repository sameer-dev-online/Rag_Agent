from typing import List, Dict, Any, Optional
from openai import OpenAI
from supabase import create_client, Client
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.exceptions import VectorStoreException


class VectorService:
    """
    Service for vector operations using native pgvector via supabase-py.
    Handles document chunking, embedding generation, and similarity search.
    """

    def __init__(self):
        """Initialize VectorService with Supabase client and OpenAI client."""
        try:
            # Initialize Supabase client with service role key for full access
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )

            # Initialize OpenAI client for embeddings
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

            # Initialize text splitter for chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )

        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to initialize VectorService: {str(e)}",
                details={"error": str(e)}
            )

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a given text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=settings.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to generate embedding: {str(e)}",
                details={"error": str(e)}
            )

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks using RecursiveCharacterTextSplitter.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        try:
            chunks = self.text_splitter.split_text(text)
            return chunks
        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to chunk text: {str(e)}",
                details={"error": str(e)}
            )

    def add_document_embeddings(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Chunk text, generate embeddings, and store in vector database.

        Args:
            document_id: Unique identifier for the document
            text: Document text to embed
            metadata: Additional metadata to store with embeddings

        Returns:
            Number of chunks created
        """
        try:
            # Delete existing embeddings for this document (idempotent)
            self.delete_document_embeddings(document_id)

            # Chunk the text
            chunks = self.chunk_text(text)

            if not chunks:
                return 0

            # Prepare records for batch insertion
            records = []
            for idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self._generate_embedding(chunk)

                # Prepare record
                record = {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "chunk_text": chunk,
                    "embedding": embedding,
                    "metadata": metadata or {}
                }
                records.append(record)

            # Batch insert all records
            if records:
                self.supabase.table("embeddings").insert(records).execute()

            return len(chunks)

        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to add document embeddings: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )

    def similarity_search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity via RPC function.

        Args:
            query: Search query text
            top_k: Number of results to return (defaults to settings.top_k_retrieval)
            filter_metadata: Optional metadata filters (supports user_id and document_id)

        Returns:
            List of matching chunks with metadata and similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Set default top_k
            if top_k is None:
                top_k = settings.top_k_retrieval

            # Extract filter values
            filter_user_id = None
            filter_document_id = None
            if filter_metadata:
                filter_user_id = filter_metadata.get("user_id")
                filter_document_id = filter_metadata.get("document_id")

            # Call RPC function for similarity search
            result = self.supabase.rpc(
                "match_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "filter_document_id": filter_document_id,
                    "filter_user_id": filter_user_id,
                    "match_threshold": 0.0
                }
            ).execute()

            # Format results to match expected interface
            formatted_results = []
            for row in result.data or []:
                formatted_results.append({
                    "id": row["id"],
                    "similarity_score": float(row["similarity"]),
                    "chunk_text": row["chunk_text"],
                    "document_id": row["document_id"],
                    "chunk_index": row["chunk_index"],
                    "metadata": row["metadata"]
                })

            return formatted_results

        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to perform similarity search: {str(e)}",
                details={"error": str(e), "query": query}
            )

    def delete_document_embeddings(self, document_id: str) -> None:
        """
        Delete all embeddings associated with a document.

        Args:
            document_id: Document ID to delete embeddings for
        """
        try:
            self.supabase.table("embeddings").delete().eq(
                "document_id", document_id
            ).execute()
        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to delete document embeddings: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )
