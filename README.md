# VakeelAI – Indian Legal AI Assistant

**Nyaya** is a RAG-based AI legal research assistant that answers questions about Indian law, strictly grounded in a knowledge base you upload. Bring your own API key, upload legal documents, and get accurate, cited answers.

## Features

- 🤖 **Multi-Provider LLM Support** – OpenAI, Anthropic (Claude), Google Gemini
- 📚 **Knowledge Base Management** – Upload PDFs, DOCX, TXT, HTML legal documents
- 🔍 **Hybrid Retrieval** – Vector similarity + BM25 keyword search with Reciprocal Rank Fusion
- 📖 **Structural Chunking** – Splits by Section/Article, keeps provisos attached
- 🔄 **IPC → BNS Mapping** – Automatically maps old law references to new codes
- 🛡️ **Guardrails** – Scope guard, citation verification, harm detection
- 🔐 **Secure** – Encrypted API key storage, never logged or exposed
- 💬 **Streaming Chat** – Real-time SSE response streaming with citations
- 📱 **Responsive UI** – Clean white design, mobile-friendly

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e .

# Copy env template
copy ..\.env.example .env  # Windows
# cp ../.env.example .env  # Linux/Mac

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Open the App
Navigate to `http://localhost:5173`

## Getting API Keys

| Provider | How to Get |
|----------|-----------|
| **OpenAI** | Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys) → Create key |
| **Anthropic** | Go to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) → Create key |
| **Google Gemini** | Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → Create key |

## Uploading Documents

1. Navigate to **Knowledge Base** (sidebar or onboarding)
2. Select a document category (Statute, Supreme Court, etc.)
3. Drag-and-drop or click to upload PDF/DOCX/TXT/HTML files
4. Wait for ingestion (extracting → chunking → embedding → indexing)
5. Start asking questions!

### Recommended documents to upload:
- Constitution of India
- Bharatiya Nyaya Sanhita (BNS), 2023
- Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023
- Indian Contract Act, 1872
- Negotiable Instruments Act, 1881
- Code of Civil Procedure, 1908
- Consumer Protection Act, 2019

## IPC-BNS Mapping

The app automatically maps old Indian Penal Code (IPC) sections to new Bharatiya Nyaya Sanhita (BNS) sections. To extend the mapping:

Edit `backend/data/ipc_bns_map.json` and add entries:

```json
{"ipc": "302", "bns": "103", "title": "Punishment for murder"}
```

Similarly for CrPC → BNSS and Evidence Act → BSA mappings.

## Project Structure

```
nyaya/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── api/                  # API route handlers
│   │   │   ├── chat.py           # Chat with SSE streaming
│   │   │   ├── keys.py           # API key management
│   │   │   ├── documents.py      # Document upload/management
│   │   │   └── health.py         # Health check
│   │   ├── core/                 # Configuration & security
│   │   │   ├── config.py         # Settings from .env
│   │   │   ├── crypto.py         # Fernet encryption
│   │   │   └── security.py       # Rate limiting, validation
│   │   ├── llm/                  # LLM provider adapters
│   │   │   ├── base.py           # Abstract interface
│   │   │   ├── openai_client.py
│   │   │   ├── anthropic_client.py
│   │   │   ├── gemini_client.py
│   │   │   └── factory.py
│   │   ├── rag/                  # RAG pipeline
│   │   │   ├── ingest.py         # Full ingestion pipeline
│   │   │   ├── chunking.py       # Structural document chunking
│   │   │   ├── ocr.py            # Text extraction + OCR
│   │   │   ├── retriever.py      # Hybrid search + RRF
│   │   │   ├── reranker.py       # Cross-encoder re-ranking
│   │   │   ├── query_rewrite.py  # Synonym expansion, IPC→BNS
│   │   │   ├── generator.py      # Answer generation
│   │   │   └── guardrails.py     # Pre/post classification
│   │   └── db/                   # SQLite models & session
│   ├── prompts/system_prompt.txt
│   ├── data/ipc_bns_map.json
│   └── pyproject.toml
├── frontend/
│   └── src/
│       ├── App.tsx               # Root app with routing
│       ├── pages/                # Onboarding, Chat, KB, Settings
│       ├── lib/                  # API client, types
│       └── styles/               # CSS per page
├── knowledge_base/               # Drop documents here (auto-watched)
├── .env.example
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/keys/status` | Connection status (never returns key) |
| GET | `/api/keys/models` | Available providers/models |
| POST | `/api/keys/test` | Test an API key |
| POST | `/api/keys` | Save encrypted key |
| DELETE | `/api/keys` | Delete stored key |
| POST | `/api/documents` | Upload document (multipart) |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{id}` | Delete document |
| GET | `/api/documents/progress/{job_id}` | Ingestion progress |
| POST | `/api/chat` | Chat (SSE stream) |
| GET | `/api/sessions` | List chat sessions |
| GET | `/api/sources/{chunk_id}` | Get source passage |
| POST | `/api/feedback` | Submit feedback |

## Security

- API keys encrypted at rest with Fernet/AES
- Machine-generated encryption key stored locally
- Keys never returned in API responses
- Rate limiting on key endpoints
- CORS restricted to frontend origin
- Prompt injection defense in system prompt
