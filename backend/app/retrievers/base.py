"""
Abstract Base Class for RAG Retrievers.
Every retrieval technique inherits from this and implements search().
"""
import logging
from abc import ABC, abstractmethod
from typing import Any

from ..qdrant_service import qdrant_service as default_qdrant_service

logger = logging.getLogger(__name__)


class BaseRetriever(ABC):
    """Abstract base class for all RAG retrieval strategies."""

    name: str = ""
    label: str = ""
    description: str = ""

    def __init__(
        self,
        qdrant_service=None,
        user_id: int | None = None,
        openrouter_api_key: str | None = None,
    ):
        self.qs = qdrant_service or default_qdrant_service
        self.user_id = user_id
        self.openrouter_api_key = openrouter_api_key

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
        """
        raise NotImplementedError

    def get_info(self) -> dict[str, Any]:
        """Return retriever metadata for UI strategy selectors."""
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
        }
