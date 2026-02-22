import vecs
from typing import List, Dict, Any
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.exceptions import VectorStoreException


class VectorService:
    """
    Service for vector operations using Supabase vecs library.
    Handles document chunking, embedding generation, and similarity search.
    """

    def __init__(self):
        """Initialize VectorService with vecs client and OpenAI client."""
        try:
            # Initialize vecs client
            self.vx = vecs.create_client(settings.database_url)

            # Initialize OpenAI client for embeddings
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

            # Initialize text splitter for chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )

            # Get or create the document embeddings collection
            self.collection = self._get_or_create_collection()

        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to initialize VectorService: {str(e)}",
                details={"error": str(e)}
            )

    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            # Try to get existing collection
            collections = self.vx.list_collections()
            collection_name = "document_embeddings"

            if collection_name in [c.name for c in collections]:
                return self.vx.get_collection(name=collection_name)
            else:
                # Create new collection with specified dimension
                return self.vx.create_collection(
                    name=collection_name,
                    dimension=settings.embedding_dimension
                )
        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to get or create collection: {str(e)}",
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
        metadata: Dict[str, Any] = None
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
            # Chunk the text
            chunks = self.chunk_text(text)

            # Prepare records for insertion
            records = []
            for idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self._generate_embedding(chunk)

                # Prepare metadata
                chunk_metadata = {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "chunk_text": chunk,
                    **(metadata or {})
                }

                # Create record with unique ID
                record_id = f"{document_id}_{idx}"
                records.append((record_id, embedding, chunk_metadata))

            # Upsert records to collection
            if records:
                self.collection.upsert(records=records)
                # Create index if it doesn't exist (for performance)
                self.collection.create_index()

            return len(chunks)

        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to add document embeddings: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )

    def similarity_search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query: Search query text
            top_k: Number of results to return (defaults to settings.top_k_retrieval)
            filter_metadata: Optional metadata filters

        Returns:
            List of matching chunks with metadata and similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Set default top_k
            if top_k is None:
                top_k = settings.top_k_retrieval

            # Perform similarity search
            results = self.collection.query(
                data=query_embedding,
                limit=top_k,
                filters=filter_metadata,
                include_value=True,
                include_metadata=True
            )

            # Format results
            formatted_results = []
            for record_id, distance, metadata in results:
                formatted_results.append({
                    "id": record_id,
                    "similarity_score": float(1 - distance),  # Convert distance to similarity
                    "chunk_text": metadata.get("chunk_text", ""),
                    "document_id": metadata.get("document_id", ""),
                    "chunk_index": metadata.get("chunk_index", 0),
                    "metadata": metadata
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
            # Delete by filtering on document_id in metadata
            self.collection.delete(filters={"document_id": {"$eq": document_id}})
        except Exception as e:
            raise VectorStoreException(
                message=f"Failed to delete document embeddings: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )
