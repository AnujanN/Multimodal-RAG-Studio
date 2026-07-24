"""
Preset input texts for the playground.
All in Markdown format — LLMs and chunkers work better with structured text.
"""

PRESETS: dict[str, dict] = {
    "technical_article": {
        "label": "Technical Article",
        "description": "A Markdown-formatted article about transformer architecture",
        "text": """# Understanding Transformer Architecture in Modern NLP

## Introduction

The Transformer architecture, introduced in the seminal paper "Attention Is All You Need" (Vaswani et al., 2017), has fundamentally revolutionized the field of natural language processing. Unlike its predecessors — recurrent neural networks (RNNs) and long short-term memory networks (LSTMs) — the Transformer relies entirely on attention mechanisms to draw global dependencies between input and output.

This shift away from sequential processing has enabled unprecedented parallelization during training, making it feasible to train models on massive corpora within reasonable timeframes.

## Core Components

### Self-Attention Mechanism

The self-attention mechanism allows each token in a sequence to attend to all other tokens simultaneously. For a sequence of n tokens, self-attention computes three matrices — Query (Q), Key (K), and Value (V) — from the input embeddings.

The attention score is computed as:

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
```

Where d_k is the dimension of the key vectors. The scaling factor prevents vanishing gradients when d_k is large.

### Multi-Head Attention

Rather than performing a single attention function, multi-head attention projects Q, K, V into h different subspaces and performs attention in parallel. The outputs are then concatenated and projected back:

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W_O
```

This allows the model to jointly attend to information from different representation subspaces at different positions.

### Feed-Forward Networks

Each attention sub-layer is followed by a position-wise feed-forward network:

```
FFN(x) = max(0, xW_1 + b_1) * W_2 + b_2
```

These networks apply the same transformation to each position independently.

## Positional Encoding

Since the Transformer has no recurrence, positional information must be explicitly injected. Sinusoidal positional encodings are added to the input embeddings:

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

## Key Performance Benchmarks

| Model | Parameters | BLEU (WMT En-De) | Training Time |
|-------|-----------|-------------------|---------------|
| Transformer Base | 65M | 27.3 | 12h (8 GPUs) |
| Transformer Big | 213M | 28.4 | 3.5d (8 GPUs) |
| BERT Large | 340M | N/A | 4d (64 TPUs) |
| GPT-3 | 175B | N/A | N/A (proprietary) |

## Applications and Variants

### BERT and Bidirectional Models

BERT (Bidirectional Encoder Representations from Transformers) uses only the encoder stack and trains with masked language modeling. This bidirectional context makes it highly effective for:

- Text classification
- Named entity recognition
- Question answering
- Sentiment analysis

### GPT Family and Autoregressive Models

The GPT family uses only the decoder stack in an autoregressive fashion, predicting the next token at each step. Key characteristics:

- Causal attention masks prevent information leakage from future tokens
- Scale dramatically improves performance (GPT-3: 175B parameters)
- Few-shot and zero-shot capabilities emerge at scale

## Conclusion

The Transformer's impact on NLP cannot be overstated. Its attention-based approach has become the de facto standard for language modeling, machine translation, summarization, and virtually every other NLP task. As we scale these models, emergent capabilities continue to surprise the research community.
""",
    },
    "business_report": {
        "label": "Business Report",
        "description": "Q3 financial report with KPIs, tables, and bullet lists",
        "text": """# Q3 2024 Business Performance Report

**Prepared by:** Strategy & Analytics Team
**Date:** October 15, 2024
**Classification:** Internal — Confidential

---

## Executive Summary

The third quarter of 2024 demonstrated robust performance across all key business units, with total revenue reaching $4.2M — a 35% year-over-year increase. Customer acquisition costs decreased by 18% while retention rates improved to 94%. The APAC region emerged as our fastest-growing market, contributing 28% of total revenue.

---

## Key Performance Indicators

| Metric | Q3 2024 | Q3 2023 | Change |
|--------|---------|---------|--------|
| Total Revenue | $4.2M | $3.1M | +35% |
| Gross Margin | 68% | 61% | +7pp |
| Net Margin | 18% | 12% | +6pp |
| MRR | $1.4M | $1.0M | +40% |
| Customer Count | 2,847 | 2,103 | +35% |
| NPS Score | 72 | 65 | +7 |
| CAC | $320 | $390 | -18% |
| LTV:CAC Ratio | 4.8 | 3.2 | +50% |

---

## Revenue Breakdown by Region

### North America
North America remains our largest market at 48% of total revenue ($2.02M). Enterprise segment growth was particularly strong, driven by three major contract renewals and two new Fortune 500 customers onboarded in August.

Key highlights:
- Enterprise contracts up 42% YoY
- SMB segment grew 28% YoY
- Average contract value increased from $8,400 to $11,200
- Churn rate dropped from 8% to 4.8%

### APAC
The Asia-Pacific region delivered exceptional results, growing 62% year-over-year to reach $1.18M.

Key highlights:
- Japan market entered with 3 enterprise clients
- Australia expanded to 127 customers (from 54)
- India SMB tier launched in July — already 340 customers
- Singapore office headcount doubled to 12

### Europe
European revenue grew 22% to $0.84M.

Key highlights:
- GDPR compliance feature release drove 15 new enterprise wins
- Germany and UK account for 71% of European revenue
- France underperformed — dedicated sales resource being evaluated

---

## Product Performance

### Core Platform
- 99.97% uptime achieved (target: 99.9%)
- Average API response time: 87ms (down from 134ms in Q2)
- 14 new features shipped across 6 releases

### New Products Launched in Q3
1. **Analytics Dashboard v2.0** — 1,204 active users within 30 days
2. **AI-Powered Insights Module** — Beta with 89 enterprise customers
3. **Mobile Application** — 8,200 downloads, 4.6★ app store rating

---

## Operational Highlights

### Headcount
- Total employees: 187 (up from 142 in Q3 2023)
- Engineering: 94 (50% of headcount)
- Sales & Marketing: 41
- Customer Success: 28
- G&A: 24

### Notable Achievements
- ISO 27001 certification completed
- SOC 2 Type II audit passed
- Engineering velocity improved 31% after Agile transformation

---

## Q4 2024 Outlook

### Revenue Targets
| Metric | Q4 Target | Full-Year Target |
|--------|-----------|-----------------|
| Revenue | $4.8M | $15.8M |
| New Customers | 380 | 1,200 |
| Enterprise Wins | 12 | 38 |

### Strategic Priorities
1. Launch in 3 new European markets (France, Netherlands, Sweden)
2. Complete Series B fundraising ($25M target)
3. Release AI Insights Module to general availability
4. Achieve SOC 2 Type II certification renewal
""",
    },
    "code_documentation": {
        "label": "Code Documentation",
        "description": "API documentation with function signatures and examples",
        "text": """# ChunkerSDK API Reference

Version: 2.1.0 | Python 3.10+

## Installation

```bash
pip install chunker-sdk
# or with uv:
uv add chunker-sdk
```

---

## Quick Start

```python
from chunker_sdk import ChunkerClient

client = ChunkerClient(api_key="your-api-key")

# Chunk a document
result = client.chunk(
    text="Your document text here...",
    technique="semantic_chunker",
    params={"similarity_threshold": 0.5}
)

for chunk in result.chunks:
    print(f"Chunk {chunk.index}: {len(chunk.text)} chars")
```

---

## Core Classes

### ChunkerClient

Main entry point for the SDK.

```python
class ChunkerClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.chunker.io/v2",
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        ...
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| api_key | str | required | Your API key from the dashboard |
| base_url | str | "https://..." | API base URL |
| timeout | int | 30 | Request timeout in seconds |
| max_retries | int | 3 | Number of retry attempts on failure |

---

### chunk()

Splits text using the specified chunking technique.

```python
def chunk(
    self,
    text: str,
    technique: str = "recursive_chunker",
    params: dict | None = None,
    source_type: str = "custom",
) -> ChunkResult:
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| text | str | required | Input text to chunk |
| technique | str | "recursive_chunker" | Name of chunking technique |
| params | dict | None | Technique-specific parameters |
| source_type | str | "custom" | Source label for logging |

**Returns:** `ChunkResult`

**Raises:**
- `ChunkerAPIError` — API returned an error response
- `ChunkerTimeoutError` — Request timed out after retries
- `ChunkerValidationError` — Invalid parameters

**Example:**

```python
result = client.chunk(
    text=long_document,
    technique="table_aware_chunker",
    params={},
)

print(f"Created {result.stats.total_chunks} chunks")
print(f"Average size: {result.stats.avg_chunk_size:.0f} chars")
print(f"Processing time: {result.processing_time_ms:.1f}ms")
```

---

### chunk_file()

Upload and chunk a file directly.

```python
async def chunk_file(
    self,
    file_path: str | Path,
    technique: str = "heading_based_chunker",
    params: dict | None = None,
) -> ChunkResult:
```

**Supported file types:** `.pdf`, `.docx`, `.txt`, `.md`, `.csv`, `.json`, `.html`, `.png`, `.jpg`

**Example:**

```python
import asyncio
from chunker_sdk import ChunkerClient

async def process_report():
    client = ChunkerClient(api_key="your-key")
    result = await client.chunk_file(
        file_path="./quarterly_report.pdf",
        technique="table_aware_chunker",
    )
    return result.chunks

chunks = asyncio.run(process_report())
```

---

## Data Models

### ChunkResult

```python
@dataclass
class ChunkResult:
    id: str                     # Unique result ID
    technique: str              # Technique used
    chunks: list[Chunk]         # List of chunk objects
    stats: ChunkStats           # Aggregate statistics
    processing_time_ms: float   # Total processing time
```

### Chunk

```python
@dataclass
class Chunk:
    index: int        # Zero-based chunk index
    text: str         # Chunk content
    char_count: int   # Character count
    token_count: int  # Estimated token count
```

### ChunkStats

```python
@dataclass
class ChunkStats:
    total_chunks: int       # Number of chunks
    total_characters: int   # Total input characters
    avg_chunk_size: float   # Mean chunk size in chars
    min_chunk_size: int     # Smallest chunk
    max_chunk_size: int     # Largest chunk
```

---

## Available Techniques

### Basic
- `naive_chunker` — Line-break splitting
- `fixed_size_chunker` — Fixed character count (param: `chunk_size`)
- `sliding_window_chunker` — With overlap (params: `chunk_size`, `overlap`)
- `sentence_chunker` — NLTK sentence tokenization (param: `sentences_per_chunk`)
- `paragraph_chunker` — Paragraph groups (param: `max_paragraphs`)
- `page_chunker` — Page boundary splitting

### Advanced
- `table_aware_chunker` — Preserves table structures
- `heading_based_chunker` — Markdown/HTML headings (param: `max_heading_level`)
- `content_aware_chunker` — Mixed content type detection
- `entity_based_chunker` — Named entity grouping (param: `entity_types`)

### AI-Powered
- `semantic_chunker` — Embedding similarity (param: `similarity_threshold`)
- `token_based_chunker` — Token count splitting (param: `max_tokens`)
- `hybrid_chunker` — Combined approach (params: `max_chunk_size`, `heading_level`)

---

## Error Handling

```python
from chunker_sdk.exceptions import ChunkerAPIError, ChunkerTimeoutError

try:
    result = client.chunk(text=document, technique="semantic_chunker")
except ChunkerAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
except ChunkerTimeoutError:
    print("Request timed out. Try increasing timeout parameter.")
```
""",
    },
    "mixed_content": {
        "label": "Mixed Content",
        "description": "Document combining prose, tables, code, lists, and structured data",
        "text": """# Annual Technology Review 2024

## Overview

This document provides a comprehensive review of technology trends, tool evaluations, and infrastructure decisions made throughout 2024. It combines qualitative analysis with performance data, code examples, and structured recommendations.

---

## Infrastructure Performance

### Cloud Cost Analysis

Monthly cloud costs by service category for Q3 2024:

| Service | Provider | Monthly Cost | vs Budget | Trend |
|---------|----------|-------------|-----------|-------|
| Compute (EC2/GCE) | AWS | $12,400 | +8% | ↑ |
| Database (RDS) | AWS | $3,200 | -5% | ↓ |
| Storage (S3) | AWS | $890 | -12% | ↓ |
| CDN | CloudFront | $340 | +2% | → |
| AI/ML APIs | OpenAI | $5,100 | +41% | ↑↑ |
| **Total** | | **$21,930** | **+7%** | **↑** |

### Performance Benchmarks

API endpoint response time distribution (p50/p95/p99):

| Endpoint | p50 | p95 | p99 | SLA Target |
|----------|-----|-----|-----|------------|
| /api/search | 45ms | 120ms | 340ms | p95 < 200ms ✅ |
| /api/chunk | 180ms | 890ms | 2100ms | p95 < 1000ms ✅ |
| /api/upload | 1.2s | 4.8s | 12s | p95 < 10s ✅ |
| /api/embed | 95ms | 420ms | 980ms | p95 < 500ms ✅ |

---

## Technology Decisions

### Vector Database Evaluation

During Q2, we evaluated four vector databases for our RAG pipeline:

**Qdrant** was selected based on the following factors:
- Native filtering with HNSW index
- Rust-based, memory efficient
- Excellent Python client with FastEmbed integration
- On-premise and cloud options

Alternatives evaluated:
1. **Pinecone** — Excellent managed service, but vendor lock-in concerns and pricing at scale
2. **Weaviate** — Feature-rich with GraphQL API, but complex operational overhead
3. **Chroma** — Simple API ideal for prototyping, but not production-ready at our scale
4. **pgvector** — Tight Postgres integration, limited to ~1M vectors efficiently

### Chunking Strategy

After extensive testing with our document corpus, we adopted a **hybrid approach**:

```python
from app.chunkers import HybridChunker, SemanticChunker

# For structured documents (PDFs with headings)
primary = HybridChunker()
chunks = primary.chunk(
    text=document,
    max_chunk_size=800,
    heading_level=2,
)

# For unstructured prose
fallback = SemanticChunker()
chunks = fallback.chunk(
    text=document,
    similarity_threshold=0.55,
    min_chunk_sentences=2,
)
```

Benchmark results on our test corpus (500 documents):

| Strategy | Retrieval Precision@5 | Avg Chunks | Processing Time |
|----------|----------------------|------------|-----------------|
| Fixed Size (500 chars) | 61% | 45 | 12ms |
| Paragraph | 67% | 23 | 8ms |
| Semantic | 79% | 31 | 340ms |
| Hybrid (selected) | 82% | 28 | 95ms |

---

## Engineering Initiatives

### Q4 2024 Roadmap

**High Priority:**
- [ ] Migrate to async FastAPI throughout
- [ ] Implement request-level caching with Redis
- [ ] Add OpenTelemetry tracing to all services

**Medium Priority:**
- [ ] Upgrade PostgreSQL from 14 to 16
- [ ] Evaluate Rust rewrite of chunking engine for performance
- [ ] Add multi-tenant support with row-level security

**Low Priority:**
- [ ] Explore WebAssembly for client-side chunking
- [ ] Investigate LLM-assisted chunking quality improvements

### Code Quality Metrics

```bash
# Run the full quality suite
$ make lint
ruff check . --fix          # 0 violations
mypy app/                   # 0 type errors
pytest tests/ -v            # 127 passed, 0 failed

# Coverage report
$ pytest --cov=app --cov-report=term-missing
Coverage: 94.3% (target: 90%)
```

---

## Recommendations

Based on our 2024 learnings, we recommend the following for the engineering organization in 2025:

### Toolchain
- Standardize on **uv** for all Python dependency management
- Adopt **Ruff** as the single linter/formatter (replaces isort, black, flake8)
- Use **FastEmbed** for all local embedding needs (avoid heavyweight transformer dependencies)

### Architecture
- Move to an event-driven architecture for async document processing
- Implement chunking as a dedicated microservice with its own scaling profile
- Cache embedding computations in Redis with 24h TTL

### Team
- Embed an AI Engineer in each product squad by Q2 2025
- Establish a RAG quality framework with automated regression testing
- Run quarterly chunking strategy reviews against evolving document corpus
""",
    },
}


def get_preset(name: str) -> dict | None:
    return PRESETS.get(name)


def list_presets() -> list[dict]:
    return [
        {
            "name": k,
            "label": v["label"],
            "description": v["description"],
            "preview": v["text"][:150] + "...",
        }
        for k, v in PRESETS.items()
    ]
