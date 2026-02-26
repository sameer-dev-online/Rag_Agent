/**
 * Document metadata from backend
 */
export interface Document {
  id: string;
  user_id: string;
  filename: string;
  content_type: string;
  content_length: number;
  num_chunks: number;
  created_at: string;
}

/**
 * Response from POST /api/v1/documents
 */
export interface DocumentUploadResponse {
  document: Document;
}

/**
 * Upload progress tracking
 */
export interface UploadProgress {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  document?: Document;
  error?: string;
}
