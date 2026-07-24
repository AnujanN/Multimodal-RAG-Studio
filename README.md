# Chunking Strategies Playground

An interactive playground to explore, test, and compare **21 text chunking techniques** for building higher-precision RAG systems.

---

## Features

- ⚡ **21 Chunking Techniques**: Basic (6), Advanced (8), and AI-Powered (7)
- 📄 **Docling OCR Parsing**: Supports PDFs (text/scanned), DOCX, images (PNG/JPG), CSV, JSON, HTML, TXT, MD
- 🧠 **FastEmbed ONNX**: High-performance semantic chunking (`BAAI/bge-small-en-v1.5`) without PyTorch overhead
- 📊 **Visualizations & History**: Recharts distribution charts and PostgreSQL run tracking

---

## Quick Start

### 1. Dev Mode (Local hot-reload + Postgres in Docker)
```bash
make dev

# Separate terminals:
cd backend  && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```
App runs at `http://localhost:5173`.

### 2. Full Docker Mode (Containerized stack)
```bash
make prod
```
App runs at `http://localhost`.

---

## Techniques at a Glance

- **Basic**: Naive, Fixed Size, Sliding Window, Sentence, Paragraph, Page
- **Advanced**: Table Aware, Topic Based, Content Aware, Structured, Entity Based, Heading Based, Delimiter Based, List Aware
- **AI-Powered**: Recursive, Contextual, Semantic (FastEmbed), Similarity Based, Token Based (`tiktoken`), Keyword Extraction (TF-IDF), Hybrid

---

## Modular Usage in RAG Pipelines

Import chunkers directly into any Python project:

```python
from app.chunkers import SemanticChunker, HybridChunker

# FastEmbed Semantic Chunker
chunker = SemanticChunker()
chunks = chunker.chunk(text, similarity_threshold=0.55)

# Structure-Aware Hybrid Chunker
hybrid = HybridChunker()
chunks = hybrid.chunk(text, max_chunk_size=800, heading_level=2)
```

---

## License
MIT
