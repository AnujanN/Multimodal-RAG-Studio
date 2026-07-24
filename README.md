# Chunking Strategies Playground

An interactive, high-performance web application to explore, test, and compare **21 text chunking techniques** for building higher-precision RAG (Retrieval-Augmented Generation) systems.

Built with **FastAPI**, **React 18 + Vite**, **PostgreSQL**, **FastEmbed** (ONNX), and **Docling + RapidOCR**.

---

## Features

- ⚡ **21 Text Chunking Techniques**: Basic (6), Advanced (8), and AI-Powered (7)
- 📄 **Document Upload Parsing (9 Formats)**: Text/scanned PDFs, DOCX, TXT, MD, CSV, JSON, HTML, PNG, JPG, TIFF via **Docling + RapidOCR**
- 🧠 **FastEmbed Semantic Chunking**: ONNX-quantized `BAAI/bge-small-en-v1.5` embeddings (~67MB) without PyTorch overhead
- 📊 **Interactive Data Visualizations**: Recharts chunk size distribution bar chart & histogram
- 💾 **PostgreSQL Result Persistence**: Track history, execution times, character counts, and average sizes
- 📦 **Dual-Mode Docker Architecture**: Dev mode (hot-reload native + DB in Docker) and Full Prod mode (everything containerized)

---

## 21 Chunking Techniques Catalog

### 1. Basic Techniques (6)
| Technique | Description | Parameters |
|-----------|-------------|------------|
| `naive_chunker` | Splits text strictly on line breaks (`\n`) | None |
| `fixed_size_chunker` | Splits into fixed-length character blocks | `chunk_size` (default: 500) |
| `sliding_window_chunker` | Fixed-size chunks with overlapping character window | `chunk_size` (500), `overlap` (100) |
| `sentence_chunker` | NLTK sentence boundary detection | `sentences_per_chunk` (default: 3) |
| `paragraph_chunker` | Splits on double newlines (`\n\n`) | `max_paragraphs` (default: 2) |
| `page_chunker` | Splits on form-feed (`\f`) or page break markers | None |

### 2. Advanced Techniques (8)
| Technique | Description | Parameters |
|-----------|-------------|------------|
| `table_aware_chunker` | Keeps markdown tables intact while chunking surrounding prose | None |
| `topic_based_chunker` | Detects topic shifts via TF-IDF sentence window similarity | `window_size` (3), `threshold` (0.3) |
| `content_aware_chunker` | Identifies content types (lists, code blocks, prose) and splits on boundary changes | None |
| `structured_chunker` | Structure-aware parsing for HTML tags, JSON keys, or log timestamps | `format_type` (auto/html/json/log/plain) |
| `entity_based_chunker` | Groups sentences around named entities (person, location, organization, etc.) | `entity_types` (multiselect) |
| `heading_based_chunker` | Splits on markdown (`#`, `##`) or HTML (`<h1>`-`<h6>`) headings | `max_heading_level` (1-6) |
| `delimiter_based_chunker` | Splits on custom user-defined delimiter strings | `delimiter` (default: "---") |
| `list_aware_chunker` | Detects bullet and numbered lists, keeping list items together | None |

### 3. AI-Powered Techniques (7)
| Technique | Description | Parameters |
|-----------|-------------|------------|
| `recursive_chunker` | Hierarchical separator splitting (`\n\n` → `\n` → `. ` → ` `) | `chunk_size` (500), `overlap` (50) |
| `contextual_chunker` | Prepends parent heading hierarchy to each chunk for context retention | `max_heading_level` (1-6) |
| `semantic_chunker` | Cosine similarity breakpoints using FastEmbed (`bge-small-en-v1.5` ONNX) | `similarity_threshold` (0.5), `min_chunk_sentences` (2) |
| `similarity_based_chunker` | Groups consecutive sentences by cosine, Jaccard, or Levenshtein distance | `distance_metric` (cosine/jaccard/levenshtein), `threshold` |
| `token_based_chunker` | Splits by LLM token count using `tiktoken` | `max_tokens` (256), `encoding` (cl100k_base) |
| `keyword_extraction_chunker` | TF-IDF keyword extraction and sentence grouping around top keywords | `num_keywords` (5), `min_sentences_per_chunk` (2) |
| `hybrid_chunker` | Two-pass splitting: Heading-based structure split → Recursive size enforcement | `max_chunk_size` (800), `heading_level` (2) |

---

## Quick Start (WSL)

### Prerequisites
- WSL 2 (Ubuntu)
- Docker Desktop with WSL Integration enabled
- `uv` Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 18+ and npm

### Dev Mode (Native Hot-Reload + Postgres in Docker)
```bash
# 1. Start PostgreSQL database container
make dev

# 2. In Terminal 2 — Start FastAPI backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# 3. In Terminal 3 — Start React frontend
cd frontend
npm install
npm run dev

# App available at http://localhost:5173
```

### Full Docker Mode (Everything Containerized)
```bash
# Build and run Postgres, FastAPI backend, and Nginx frontend in Docker containers
make prod

# App available at http://localhost
```

### Management Commands
```bash
make down     # Stop all containers
make clean    # Stop containers and wipe PostgreSQL volume
make help     # View all available make targets
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/techniques` | List all 21 chunking techniques grouped by category |
| `POST` | `/api/chunk` | Process text with selected technique & save results |
| `GET` | `/api/presets` | Get sample preset texts |
| `GET` | `/api/presets/{name}` | Get detailed text for a specific preset |
| `POST` | `/api/upload` | Upload file (PDF/DOCX/PNG/etc.) → extract Markdown text |
| `GET` | `/api/history` | List past chunking runs |
| `DELETE` | `/api/history/{id}` | Delete a history item |
| `GET` | `/api/health` | API health check |

---

## Modular Usage in RAG Pipelines

All chunker classes inherit from `BaseChunker` and can be imported directly into Python RAG pipelines without external server dependencies:

```python
from app.chunkers import SemanticChunker, HybridChunker

# Semantic chunker using FastEmbed
chunker = SemanticChunker()
chunks = chunker.chunk(text, similarity_threshold=0.55)

# Hybrid chunker
hybrid = HybridChunker()
chunks = hybrid.chunk(text, max_chunk_size=800, heading_level=2)
```

---

## License

MIT
