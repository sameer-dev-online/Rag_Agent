-- Migration: Create embeddings table with native pgvector
-- This replaces the vecs library abstraction with native pgvector operations

-- Create embeddings table with native vector column
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_document_chunk UNIQUE (document_id, chunk_index)
);

-- Create HNSW index for cosine similarity
-- HNSW has better performance than IVFFlat and works well on empty tables
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw ON embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Create indexes for common filters
CREATE INDEX IF NOT EXISTS idx_embeddings_document_id ON embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_metadata_user_id ON embeddings((metadata->>'user_id'));

-- Create RPC function for similarity search
-- PostgREST does not support pgvector operators (<=>), so we use an RPC function
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    filter_document_id UUID DEFAULT NULL,
    filter_user_id TEXT DEFAULT NULL,
    match_threshold FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INTEGER,
    chunk_text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql STABLE
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.document_id,
        e.chunk_index,
        e.chunk_text,
        e.metadata,
        (1 - (e.embedding <=> query_embedding))::FLOAT AS similarity
    FROM embeddings e
    WHERE
        (filter_document_id IS NULL OR e.document_id = filter_document_id)
        AND (filter_user_id IS NULL OR e.metadata->>'user_id' = filter_user_id)
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;

-- Enable Row Level Security
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view embeddings for their documents"
    ON embeddings FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM documents
        WHERE documents.id = embeddings.document_id
        AND documents.user_id = current_setting('app.current_user_id', true)
    ));

CREATE POLICY "Users can insert embeddings for their documents"
    ON embeddings FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM documents
        WHERE documents.id = embeddings.document_id
        AND documents.user_id = current_setting('app.current_user_id', true)
    ));

CREATE POLICY "Users can delete embeddings for their documents"
    ON embeddings FOR DELETE
    USING (EXISTS (
        SELECT 1 FROM documents
        WHERE documents.id = embeddings.document_id
        AND documents.user_id = current_setting('app.current_user_id', true)
    ));

CREATE POLICY "Service role has full access to embeddings"
    ON embeddings FOR ALL
    USING (current_setting('role', true) = 'service_role')
    WITH CHECK (current_setting('role', true) = 'service_role');

-- Grant execute on the RPC function
GRANT EXECUTE ON FUNCTION match_embeddings TO authenticated, service_role;
