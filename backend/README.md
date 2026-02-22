# RAG Backend API

Production-ready RAG (Retrieval-Augmented Generation) backend using FastAPI, PydanticAI, LangChain, and Supabase.

## Features

- **Document Upload & Processing**: Upload PDF, DOCX, and TXT files
- **Vector Search**: Semantic search using OpenAI embeddings and pgvector
- **Conversation Memory**: Persistent conversation history in Supabase
- **AI Agent**: PydanticAI-powered assistant with retrieval capabilities
- **API Key Authentication**: Simple header-based authentication
- **Standard Response Format**: Consistent JSON responses across all endpoints

## Tech Stack

- **Backend Framework**: FastAPI (async)
- **Agent Framework**: PydanticAI with OpenAI models
- **Document Processing**: LangChain (loaders, chunking, embeddings)
- **Database**: Supabase Postgres + pgvector
- **Vector Operations**: `vecs` library (Supabase's official Python client)
- **Authentication**: API Key (header-based)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings (Pydantic Settings)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # API endpoints
│   │   └── dependencies.py        # API key auth dependency
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── response.py            # Standard response format
│   │   ├── chat.py                # Chat schemas
│   │   └── document.py            # Document schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py         # RAG orchestration
│   │   ├── memory_service.py      # Conversation/message CRUD
│   │   ├── vector_service.py      # Vector operations (vecs)
│   │   └── document_service.py    # Document parsing & processing
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py               # PydanticAI agent
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── middleware.py          # Request/response middleware
│   └── utils/
│       ├── __init__.py
│       └── helpers.py             # Utility functions
├── migrations/
│   └── 20260222000000_initial_schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Supabase account with project created
- OpenAI API key

### 1. Clone/Navigate to Project

```bash
cd /mnt/c/Users/ALPHA/OneDrive/Documents/rag_agent/backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# API Configuration
API_KEY=your-secret-api-key-here
API_V1_PREFIX=/api/v1

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_publishable_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO

# RAG Config
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
LLM_MODEL=gpt-4o
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
MAX_MEMORY_MESSAGES=8
```

### 5. Database Setup

The database migration has already been applied. To verify:

```bash
# Check if tables exist using Supabase dashboard or CLI
```

### 6. Run the Application

**Development Mode** (with auto-reload):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode**:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 7. Access the API

- **Base URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (development only)
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### 1. Health Check

**GET** `/api/v1/health`

No authentication required.

**Response:**
```json
{
  "success": true,
  "message": "Service is running",
  "status": 200,
  "data": {"status": "healthy"}
}
```

### 2. Chat

**POST** `/api/v1/chat`

Send a message to the RAG agent.

**Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What is the company policy on remote work?",
  "user_id": "user123",
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message processed successfully",
  "status": 200,
  "data": {
    "conversation_id": "uuid",
    "user_message": {...},
    "assistant_message": {...},
    "retrieved_contexts": [...]
  }
}
```

### 3. Upload Document

**POST** `/api/v1/documents`

Upload a document to the knowledge base.

**Headers:**
```
X-API-Key: your-api-key
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: PDF, TXT, or DOCX file
- `user_id`: string
- `title`: string (optional)

**Response:**
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "status": 201,
  "data": {
    "document_id": "uuid",
    "title": "document.pdf",
    "num_chunks": 45,
    "content_length": 12500
  }
}
```

### 4. Get Conversation

**GET** `/api/v1/conversations/{conversation_id}?user_id=user123`

Get conversation with all messages.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation retrieved successfully",
  "status": 200,
  "data": {
    "conversation": {...},
    "messages": [...]
  }
}
```

### 5. Delete Document

**DELETE** `/api/v1/documents/{document_id}?user_id=user123`

Delete a document and its embeddings.

**Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully",
  "status": 200,
  "data": null
}
```

## API Response Format

All endpoints return responses in the following standardized format:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "status": 200,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description",
  "status": 400,
  "data": null
}
```

## RAG Pipeline Flow

1. User sends message → POST /api/v1/chat
2. Create/Get conversation → MemoryService
3. Retrieve relevant context → VectorService (similarity search)
4. Get conversation history → MemoryService
5. Store user message → MemoryService
6. Combine context → Retrieved chunks + conversation history
7. Run PydanticAI agent → Generate response with context
8. Store assistant message → MemoryService
9. Return formatted response → User

## Document Upload Flow

1. User uploads file → POST /api/v1/documents
2. Parse file → DocumentService (PyPDF2, python-docx, etc.)
3. Store document → Supabase documents table
4. Chunk text → LangChain RecursiveCharacterTextSplitter
5. Generate embeddings → OpenAI text-embedding-3-small
6. Store vectors → vecs collection with metadata
7. Return success → Document ID + chunk count

## Testing

### Manual Testing with cURL

**Health Check:**
```bash
curl http://localhost:8000/api/v1/health
```

**Upload Document:**
```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H "X-API-Key: your-api-key" \
  -F "file=@test.pdf" \
  -F "user_id=test_user" \
  -F "title=Test Document"
```

**Send Chat Message:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is in the test document?",
    "user_id": "test_user"
  }'
```

### Testing with Python

```python
import httpx
import asyncio

async def test_rag_flow():
    base_url = "http://localhost:8000/api/v1"
    headers = {"X-API-Key": "your-api-key"}

    async with httpx.AsyncClient() as client:
        # Health check
        resp = await client.get(f"{base_url}/health")
        print(f"Health: {resp.json()}")

        # Upload document
        with open("test.pdf", "rb") as f:
            files = {"file": f}
            data = {"user_id": "test_user", "title": "Test Doc"}
            resp = await client.post(
                f"{base_url}/documents",
                headers=headers,
                files=files,
                data=data
            )
        print(f"Upload: {resp.json()}")

        # Chat
        chat_data = {
            "message": "What is in the test document?",
            "user_id": "test_user"
        }
        resp = await client.post(
            f"{base_url}/chat",
            headers=headers,
            json=chat_data
        )
        print(f"Chat: {resp.json()}")

asyncio.run(test_rag_flow())
```

## Database Schema

### Tables

- **conversations**: User conversations with metadata
- **messages**: Individual messages in conversations
- **documents**: Uploaded documents with content
- **Vector embeddings**: Managed by vecs library (in separate schema)

### Row Level Security (RLS)

RLS is enabled on all tables with policies for user-level data isolation. The service role bypasses RLS for backend operations.

## Error Handling

The application uses a custom exception hierarchy:

- `RAGException` (base) → 500
- `DatabaseException` → 500
- `VectorStoreException` → 500
- `ValidationException` → 400
- `NotFoundException` → 404
- `LLMException` → 502
- `AuthenticationException` → 401

All errors return the standard error response format.

## Security

### API Key Authentication

- API keys are validated via `X-API-Key` header
- Multiple keys supported (comma-separated in .env)
- Use strong, random keys in production
- Rotate keys periodically

### Environment Variables

Never commit `.env` file to version control. Always use `.env.example` as template.

### Database Security

- RLS policies protect user data
- Service role key used for backend operations
- Never expose service role key to clients

## Deployment

The application is designed to be deployment-agnostic and can run:

- Directly on a VPS with Python
- In a Docker container
- On cloud platforms (Railway, Render, Fly.io, AWS, GCP, Azure)
- As a systemd service on Linux

For production deployment, ensure:

1. Set `ENVIRONMENT=production` in .env
2. Use strong API keys
3. Configure CORS appropriately
4. Use HTTPS (reverse proxy with nginx/caddy)
5. Set up logging and monitoring
6. Use production-ready database settings

## Troubleshooting

### Common Issues

**1. Database connection error**
- Verify DATABASE_URL is correct
- Check Supabase project is active
- Ensure service role key is valid

**2. OpenAI API error**
- Verify OPENAI_API_KEY is correct
- Check API quota/billing

**3. Vector search not working**
- Ensure pgvector extension is enabled
- Check if embeddings were created during document upload

**4. Import errors**
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Logs

Application logs include:
- Request/response details
- Error traces
- Service operations

Check logs for debugging issues.

## Development

### Adding New Endpoints

1. Add route in `app/api/routes.py`
2. Create schemas in `app/schemas/`
3. Implement business logic in services
4. Add error handling
5. Test endpoint

### Modifying RAG Pipeline

Edit `app/services/rag_service.py` to customize:
- Context retrieval
- Agent prompts
- Response formatting

### Customizing Agent

Edit `app/core/agent.py` to:
- Change system prompt
- Add tools/functions
- Modify context formatting

## License

This project is private and proprietary.

## Support

For issues or questions, contact the development team.
