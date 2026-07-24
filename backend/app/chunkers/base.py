"""
Abstract base class for all chunking techniques.
Every chunker inherits from this and can be used as a standalone module
in any RAG pipeline.
"""
from abc import ABC, abstractmethod
import time
from typing import Any


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

    def chunk_timed(self, text: str, **kwargs) -> dict[str, Any]:
        """
        Run chunk() and return results with timing and statistics.
        """
        start = time.perf_counter()
        chunks = self.chunk(text, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "chunks": chunks,
            "stats": self.get_stats(chunks),
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

    def get_stats(self, chunks: list[str]) -> dict[str, Any]:
        """Compute statistics for a list of chunks."""
        if not chunks:
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
