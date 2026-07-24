"""
Abstract Base Class for RAG Retrievers.
Every retrieval technique inherits from this and implements search().
"""
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseRetriever(ABC):
    """Abstract base class for all RAG retrieval strategies."""

    name: str = ""
    label: str = ""
    description: str = ""

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        session_id: str | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context items (text chunks / images) for a user query.

        Returns a list of dicts:
        [
            {
                "text": str,
                "source_type": "text" | "image",
                "source_name": str,
                "score": float,
                "metadata": dict,
            }
        ]
        """
        raise NotImplementedError

    def get_info(self) -> dict[str, Any]:
        """Return retriever metadata for UI strategy selectors."""
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
        }
