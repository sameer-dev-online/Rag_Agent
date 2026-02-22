import io
from typing import Dict, Any, Optional, List
from fastapi import UploadFile
import PyPDF2
from docx import Document as DocxDocument
from supabase import create_client, Client

from app.config import settings
from app.core.exceptions import ValidationException, DatabaseException


class DocumentService:
    """
    Service for document parsing, storage, and management.
    Supports PDF, DOCX, and TXT file formats.
    """

    SUPPORTED_FILE_TYPES = {
        "application/pdf": "pdf",
        "text/plain": "txt",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
    }

    def __init__(self):
        """Initialize DocumentService with Supabase client."""
        try:
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to initialize DocumentService: {str(e)}",
                details={"error": str(e)}
            )

    def parse_file(self, file: UploadFile) -> str:
        """
        Parse uploaded file and extract text content.

        Args:
            file: Uploaded file object

        Returns:
            Extracted text content

        Raises:
            ValidationException: If file type is not supported or parsing fails
        """
        file_type = self._get_file_type(file)

        try:
            if file_type == "pdf":
                return self._parse_pdf(file)
            elif file_type == "docx":
                return self._parse_docx(file)
            elif file_type == "txt":
                return self._parse_txt(file)
            else:
                raise ValidationException(
                    message=f"Unsupported file type: {file.content_type}",
                    details={"content_type": file.content_type}
                )
        except ValidationException:
            raise
        except Exception as e:
            raise ValidationException(
                message=f"Failed to parse file: {str(e)}",
                details={"error": str(e), "file_type": file_type}
            )

    def _get_file_type(self, file: UploadFile) -> str:
        """
        Determine file type from content type or filename extension.

        Args:
            file: Uploaded file object

        Returns:
            File type string (pdf, txt, docx)

        Raises:
            ValidationException: If file type cannot be determined or is not supported
        """
        # Try to get type from content_type
        if file.content_type in self.SUPPORTED_FILE_TYPES:
            return self.SUPPORTED_FILE_TYPES[file.content_type]

        # Fallback to file extension
        if file.filename:
            extension = file.filename.lower().split(".")[-1]
            if extension == "pdf":
                return "pdf"
            elif extension == "txt":
                return "txt"
            elif extension == "docx":
                return "docx"

        raise ValidationException(
            message="Could not determine file type",
            details={"filename": file.filename, "content_type": file.content_type}
        )

    def _parse_pdf(self, file: UploadFile) -> str:
        """
        Extract text from PDF file using PyPDF2.

        Args:
            file: PDF file object

        Returns:
            Extracted text content
        """
        content = file.file.read()
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValidationException(
                message="No text content found in PDF",
                details={"filename": file.filename}
            )

        return full_text

    def _parse_docx(self, file: UploadFile) -> str:
        """
        Extract text from DOCX file using python-docx.

        Args:
            file: DOCX file object

        Returns:
            Extracted text content
        """
        content = file.file.read()
        docx_file = io.BytesIO(content)
        doc = DocxDocument(docx_file)

        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise ValidationException(
                message="No text content found in DOCX",
                details={"filename": file.filename}
            )

        return full_text

    def _parse_txt(self, file: UploadFile) -> str:
        """
        Read text from TXT file with encoding detection.

        Args:
            file: TXT file object

        Returns:
            File text content
        """
        content = file.file.read()

        # Try common encodings
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                text = content.decode(encoding)
                if text.strip():
                    return text
            except (UnicodeDecodeError, AttributeError):
                continue

        raise ValidationException(
            message="Could not decode text file",
            details={"filename": file.filename}
        )

    def create_document(
        self,
        user_id: str,
        title: str,
        content: str,
        file_name: str,
        file_type: str,
        source_type: str = "upload",
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store document record in database.

        Args:
            user_id: User identifier
            title: Document title
            content: Document text content
            file_name: Original file name
            file_type: File type (pdf, txt, docx)
            source_type: Source type (default: upload)
            source_metadata: Additional metadata

        Returns:
            Created document record
        """
        try:
            data = {
                "user_id": user_id,
                "title": title,
                "content": content,
                "file_name": file_name,
                "file_type": file_type,
                "source_type": source_type,
                "source_metadata": source_metadata or {}
            }

            response = self.client.table("documents").insert(data).execute()

            if not response.data:
                raise DatabaseException("Failed to create document")

            return response.data[0]

        except Exception as e:
            if isinstance(e, DatabaseException):
                raise
            raise DatabaseException(
                message=f"Failed to create document: {str(e)}",
                details={"error": str(e), "user_id": user_id}
            )

    def get_document(self, document_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a document by ID.

        Args:
            document_id: Document UUID
            user_id: Optional user ID for authorization

        Returns:
            Document record
        """
        try:
            query = self.client.table("documents").select("*").eq("id", document_id)

            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()

            if not response.data:
                raise ValidationException(
                    message="Document not found",
                    details={"document_id": document_id}
                )

            return response.data[0]

        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to get document: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )

    def get_user_documents(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all documents for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of document records
        """
        try:
            response = (
                self.client.table("documents")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return response.data or []

        except Exception as e:
            raise DatabaseException(
                message=f"Failed to get user documents: {str(e)}",
                details={"error": str(e), "user_id": user_id}
            )

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document from database.

        Args:
            document_id: Document UUID
        """
        try:
            response = (
                self.client.table("documents")
                .delete()
                .eq("id", document_id)
                .execute()
            )

            if not response.data:
                raise ValidationException(
                    message="Document not found",
                    details={"document_id": document_id}
                )

        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Failed to delete document: {str(e)}",
                details={"error": str(e), "document_id": document_id}
            )
