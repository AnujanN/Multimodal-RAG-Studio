"""
Parent-Child / Contextual Retriever.

Searches fine-grained child chunks (e.g. 200 chars) for precision similarity matching,
then retrieves the full parent section (e.g. 1000 chars) to provide rich context to the LLM.
"""
import logging
from typing import Any

from .base import BaseRetriever
from ..embeddings import embedder

logger = logging.getLogger(__name__)


class ParentChildRetriever(BaseRetriever):
    name = "parent_child"
    label = "Parent-Child Contextual Search"
    description = "Searches small sub-chunks for high-precision vector matches, then expands to return full parent section context."

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        session_id: str | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        logger.info("Running Parent-Child Retrieval for query: '%s'", query[:50])

        # 1. Embed query
        query_vector = embedder.embed_text(query)

        # 2. Search Qdrant
        raw_results = self.qs.search_dense(
            query_vector=query_vector,
            limit=limit,
            session_id=session_id,
            user_id=self.user_id,
        )

        formatted = []
        for r in raw_results:
            # Check if parent text exists in payload, fallback to item text
            parent_text = r.get("parent_text") or r.get("text", "")
            formatted.append({
                "text": parent_text,
                "child_matched_text": r.get("text", "")[:150] + "...",
                "source_type": r.get("source_type", "text"),
                "source_name": r.get("source_name", "document"),
                "score": round(r.get("_score", 0.0), 4),
                "metadata": r.get("metadata", {}),
            })

        logger.info("Parent-child retriever expanded %d matches into full context.", len(formatted))
        return formatted
