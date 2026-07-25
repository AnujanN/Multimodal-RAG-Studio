# Chunking Strategies & Multimodal RAG Studio 🚀

An interactive, high-performance web application to test, compare, and execute **21 text chunking techniques** and run a **Custom Multimodal RAG System** powered by **Qdrant Cloud**, **FastEmbed CLIP (512d)**, and **OpenRouter LLMs**.

---

## ✨ Features

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

Configure your credentials in `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://chunker:chunker_pass@postgres:5432/chunking_playground
CORS_ORIGINS=http://localhost,http://localhost:5173
MAX_UPLOAD_SIZE_MB=10

# Qdrant Cloud Credentials
QDRANT_URL=https://your-cluster-id.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=multimodal_rag_playground

# OpenRouter API Key for RAG Answer Generation
OPENROUTER_API_KEY=sk-or-v1-your_openrouter_api_key
```

*(Note: If `QDRANT_URL` is omitted, the app automatically falls back to an in-memory Qdrant client for local testing).*

---

## ⚡ Quick Start

### 1. Full Production Stack (Docker Compose)
```bash
make prod
```
- App UI: `http://localhost`
- Backend API: `http://localhost:8000/docs`
- PostgreSQL (for Beekeeper Studio / DBeaver): `localhost:5432`

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
