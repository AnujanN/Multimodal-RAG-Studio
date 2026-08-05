# Chunking Strategies & Multimodal RAG Studio 🚀

An interactive, high-performance web application to test, compare, and execute **21 text chunking techniques** and run a **Custom Multimodal RAG System** powered by **Qdrant Cloud**, **FastEmbed CLIP (512d)**, and **OpenRouter LLMs** — with **User Authentication** and **Per-User Encrypted API Key Management**.

---

## ✨ Features

- 🔑 **User Authentication & Google OAuth SSO**:
  - Secure **Email + Password login** with 24-hour signed JWT tokens.
  - **Google OAuth2 SSO** integration ("Continue with Google").
  - **Admin Mode**: `is_admin = True` users automatically use system `.env` credentials.
- 🔒 **Per-User Encrypted API Keys & Multi-Tenancy**:
  - Each user brings their own **Qdrant Cloud** and **OpenRouter** API keys.
  - **Fernet Symmetric Encryption**: Keys are encrypted at rest in PostgreSQL before storage.
  - **Isolated Qdrant Collections**: Documents are indexed in per-user isolated collections (`rag_{user_id}`).
  - **Flexible Access**: Users can skip key setup to use the **21 Chunking Strategies Lab** without entering API keys.
- 🎨 **Public Landing Page & UI**:
  - Hero showcase page highlighting features with quick **Log In** & **Sign Up Free** entry.
  - Header **⚙️ Settings** modal for updating API keys at any time.
  - **RAG Lock Overlay** for accounts without keys, with instant unlock upon entering credentials.
- ✂️ **21 Chunking Strategies**: Basic (6), Advanced (8), and AI-Powered (7) with interactive parameter controls.
- 🚀 **Multimodal RAG Studio**:
  - **Unified 512d CLIP Vector Space**: Projects both text passages and raw images into the exact same 512d vector space (`Qdrant/clip-ViT-B-32-text` & `vision`).
  - **Qdrant Cloud Integration**: Instant vector indexing and retrieval.
  - **4 Retrieval Techniques**: Dense Vector Search (Cosine), Hybrid Search (BM25 + Dense RRF), Multi-Query LLM Expansion, and Parent-Child Contextual Retrieval.
  - **OpenRouter LLM Synthesis**: Select models directly in UI (Gemini 2.0 Flash, Llama 3.3 70B, GPT-4o-mini, Claude 3.5 Haiku).
  - **Real-Time SSE Pipeline Stepper**: Live visual animation (`Parsing` ➔ `Chunking` ➔ `512d CLIP Embedding` ➔ `Qdrant Indexing`).
  - **Context Inspector**: Inspect retrieved source chunks, match scores, and document citations.
- 📄 **Docling + RapidOCR Engine**: Document parsing for PDFs (scanned/text), DOCX, PNG, JPG, CSV, JSON, HTML, TXT, and MD.
- ⚡ **Automated Pre-Downloading & Pre-Warming**: AI model weights are baked into Docker image layers during build and pre-loaded into RAM on startup for 0-latency uploads.

---

## 🛠️ Environment Configuration

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Configure system defaults in `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://chunker:chunker_pass@postgres:5432/chunking_playground
CORS_ORIGINS=http://localhost,http://localhost:5173
MAX_UPLOAD_SIZE_MB=10

# Qdrant Cloud Credentials (Admin / .env defaults)
QDRANT_URL=https://your-cluster-id.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=multimodal_rag_playground

# OpenRouter API Key for RAG Answer Generation (Admin default)
OPENROUTER_API_KEY=sk-or-v1-your_openrouter_api_key

# Auth & Security
JWT_SECRET=your-random-64char-secret-here
ENCRYPTION_KEY=your-fernet-encryption-key-here

# Google OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

*(Note: Admin users with `is_admin = True` use the `.env` keys above. Regular users enter their own keys in the app via ⚙️ Settings).*

---

## ⚡ Quick Start

### 1. Full Production Stack (Docker Compose)
```bash
make prod
```
- App UI & Landing Page: `http://localhost`
- Backend API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

### 2. Local Dev Mode (Hot-Reload)
```bash
make dev

# In separate terminals:
cd backend  && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```
- Dev App: `http://localhost:5173`

---

## 🎯 Techniques at a Glance

| Category | Available Strategies |
|---|---|
| **Basic** | Naive, Fixed Size, Sliding Window, Sentence, Paragraph, Page |
| **Advanced** | Table Aware, Topic Based, Content Aware, Structured, Entity Based, Heading Based, Delimiter Based, List Aware |
| **AI-Powered** | Recursive, Contextual, Semantic (FastEmbed), Similarity Based, Token Based (`tiktoken`), Keyword Extraction (TF-IDF), Hybrid |

---

## 📦 Modular Usage in Python

Import chunkers directly into any Python project or RAG pipeline:

```python
from app.chunkers import SemanticChunker, HybridChunker
from app.embeddings import embedder

# 1. FastEmbed Semantic Chunker
chunker = SemanticChunker()
chunks = chunker.chunk(text, similarity_threshold=0.55)

# 2. 512d CLIP Dual-Encoder Embeddings
text_vector = embedder.embed_text("FastAPI RAG application")
image_vector = embedder.embed_image_bytes(image_bytes)
```

---

## 📜 License
MIT
