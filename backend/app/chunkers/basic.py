"""
Basic chunking techniques (6):
  1. NaiveChunker          — split on newlines
  2. FixedSizeChunker      — split by character count
  3. SlidingWindowChunker  — fixed size with overlap
  4. SentenceChunker       — NLTK sentence tokenizer
  5. ParagraphChunker      — split on double newlines
  6. PageChunker           — split on form-feed / page markers
"""
import re
from typing import Any

from .base import BaseChunker


class NaiveChunker(BaseChunker):
    """Splits text on every line break (\\n)."""

    name = "naive_chunker"
    description = "Segments text by line breaks. Simple and fast — every newline creates a new chunk."
    category = "basic"
    use_cases = [
        "Note documents with structured line content",
        "Log files",
        "Line-by-line data files",
        "Quick prototyping",
    ]
    parameters = []

    def chunk(self, text: str, **kwargs) -> list[str]:
        lines = text.split("\n")
        return [line.strip() for line in lines if line.strip()]


class FixedSizeChunker(BaseChunker):
    """Splits text into equal-length character chunks."""

    name = "fixed_size_chunker"
    description = (
        "Divides text into fixed-size character chunks. "
        "Simple and predictable — ideal for uniform downstream processing."
    )
    category = "basic"
    use_cases = [
        "Uniform processing pipelines",
        "Simple vector indexing",
        "When consistent chunk sizes are required",
        "Database storage with size limits",
    ]
    parameters = [
        {
            "name": "chunk_size",
            "type": "int",
            "default": 500,
            "min": 50,
            "max": 5000,
            "description": "Number of characters per chunk",
        }
    ]

    def chunk(self, text: str, chunk_size: int = 500, **kwargs) -> list[str]:
        chunk_size = max(1, int(chunk_size))
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


class SlidingWindowChunker(BaseChunker):
    """Fixed-size chunks with configurable overlap between consecutive chunks."""

    name = "sliding_window_chunker"
    description = (
        "Creates overlapping fixed-size chunks. The overlap ensures context "
        "is preserved across chunk boundaries — critical for coherent retrieval."
    )
    category = "basic"
    use_cases = [
        "Preserving context across chunk boundaries",
        "QA systems where answers may span chunks",
        "Long document summarization",
        "Dense retrieval tasks",
    ]
    parameters = [
        {
            "name": "chunk_size",
            "type": "int",
            "default": 500,
            "min": 50,
            "max": 5000,
            "description": "Number of characters per chunk",
        },
        {
            "name": "overlap",
            "type": "int",
            "default": 100,
            "min": 0,
            "max": 1000,
            "description": "Number of overlapping characters between consecutive chunks",
        },
    ]

    def chunk(self, text: str, chunk_size: int = 500, overlap: int = 100, **kwargs) -> list[str]:
        chunk_size = max(1, int(chunk_size))
        overlap = max(0, min(int(overlap), chunk_size - 1))
        step = chunk_size - overlap
        chunks = []
        for i in range(0, len(text), step):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks


class SentenceChunker(BaseChunker):
    """Groups sentences using NLTK's sentence tokenizer."""

    name = "sentence_chunker"
    description = (
        "Uses NLTK's Punkt tokenizer to detect sentence boundaries, "
        "then groups N sentences per chunk. Respects natural language structure."
    )
    category = "basic"
    use_cases = [
        "NLP tasks requiring sentence-level context",
        "QA systems",
        "Sentiment analysis pipelines",
        "Summarization tasks",
    ]
    parameters = [
        {
            "name": "sentences_per_chunk",
            "type": "int",
            "default": 3,
            "min": 1,
            "max": 20,
            "description": "Number of sentences per chunk",
        }
    ]

    def chunk(self, text: str, sentences_per_chunk: int = 3, **kwargs) -> list[str]:
        try:
            import nltk

            try:
                sentences = nltk.sent_tokenize(text)
            except LookupError:
                nltk.download("punkt", quiet=True)
                nltk.download("punkt_tab", quiet=True)
                sentences = nltk.sent_tokenize(text)
        except ImportError:
            # Fallback: split on ". " if nltk not available
            sentences = re.split(r"(?<=[.!?])\s+", text)

        sentences_per_chunk = max(1, int(sentences_per_chunk))
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            group = sentences[i : i + sentences_per_chunk]
            chunk = " ".join(group).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class ParagraphChunker(BaseChunker):
    """Groups paragraphs (double newline separated)."""

    name = "paragraph_chunker"
    description = (
        "Splits on double newlines (paragraph breaks), then groups N paragraphs "
        "per chunk. Preserves natural document structure."
    )
    category = "basic"
    use_cases = [
        "Articles and essays",
        "Blog posts",
        "Reports with clear paragraph structure",
        "General prose documents",
    ]
    parameters = [
        {
            "name": "max_paragraphs",
            "type": "int",
            "default": 2,
            "min": 1,
            "max": 10,
            "description": "Maximum number of paragraphs per chunk",
        }
    ]

    def chunk(self, text: str, max_paragraphs: int = 2, **kwargs) -> list[str]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        max_paragraphs = max(1, int(max_paragraphs))
        chunks = []
        for i in range(0, len(paragraphs), max_paragraphs):
            group = paragraphs[i : i + max_paragraphs]
            chunk = "\n\n".join(group).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class PageChunker(BaseChunker):
    """Splits text on form-feed characters or explicit page markers."""

    name = "page_chunker"
    description = (
        "Splits on form-feed characters (\\f) or common page markers like "
        "'--- Page N ---'. Ideal for documents with clear page boundaries."
    )
    category = "basic"
    use_cases = [
        "PDF documents with page structure",
        "Book chapters",
        "Multi-page reports",
        "Documents with explicit page delimiters",
    ]
    parameters = []

    def chunk(self, text: str, **kwargs) -> list[str]:
        # Try form-feed first, then common page marker patterns
        if "\f" in text:
            pages = text.split("\f")
        else:
            pages = re.split(r"-{3,}\s*[Pp]age\s*\d+\s*-{3,}", text)

        return [p.strip() for p in pages if p.strip()]
