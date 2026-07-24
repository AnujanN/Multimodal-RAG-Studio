"""
Abstract base class for all chunking techniques.
Every chunker inherits from this and can be used as a standalone module
in any RAG pipeline.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseChunker(ABC):
    """Abstract base class for all text chunking techniques."""

    name: str = ""
    description: str = ""
    category: str = ""  # "basic" | "advanced" | "ai_powered"
    use_cases: list[str] = []
    parameters: list[dict[str, Any]] = []

    @abstractmethod
    def chunk(self, text: str, **kwargs) -> list[str]:
        """
        Split text into chunks.

        Args:
            text: The input text to chunk.
            **kwargs: Technique-specific parameters.

        Returns:
            A list of text chunks.
        """
        raise NotImplementedError

    def _validate_input(self, text: str) -> None:
        """Validate input text before processing."""
        if text is None:
            raise ValueError(f"[{self.name}] Input text cannot be None.")
        if not isinstance(text, str):
            raise TypeError(f"[{self.name}] Input text must be a string, got {type(text).__name__}.")
        if not text.strip():
            logger.warning("[%s] Input text is empty or whitespace-only.", self.name)

    def chunk_timed(self, text: str, **kwargs) -> dict[str, Any]:
        """
        Validate input, run chunk(), and return results with timing and statistics.
        """
        logger.info(
            "[%s] Starting chunking — input: %d chars, params: %s",
            self.name, len(text), kwargs or "defaults",
        )

        self._validate_input(text)

        try:
            start = time.perf_counter()
            chunks = self.chunk(text, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
        except Exception as e:
            logger.error("[%s] Chunking failed: %s", self.name, e, exc_info=True)
            raise RuntimeError(f"Chunking technique '{self.name}' failed: {e}") from e

        stats = self._compute_stats(chunks)

        logger.info(
            "[%s] Completed — %d chunks, avg %.1f chars, took %.1fms",
            self.name, stats["total_chunks"], stats["avg_chunk_size"], elapsed_ms,
        )

        return {
            "chunks": chunks,
            "stats": stats,
            "processing_time_ms": round(elapsed_ms, 3),
        }

    def get_info(self) -> dict[str, Any]:
        """Return technique metadata for the API /techniques endpoint."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "use_cases": self.use_cases,
            "parameters": self.parameters,
        }

    def _compute_stats(self, chunks: list[str]) -> dict[str, Any]:
        """Compute statistics for a list of chunks."""
        if not chunks:
            logger.debug("[%s] No chunks produced — returning zero stats.", self.name)
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0.0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
            }

        sizes = [len(c) for c in chunks]
        return {
            "total_chunks": len(chunks),
            "total_characters": sum(sizes),
            "avg_chunk_size": round(sum(sizes) / len(sizes), 1),
            "min_chunk_size": min(sizes),
            "max_chunk_size": max(sizes),
        }

    # Keep backward compat alias
    get_stats = _compute_stats
