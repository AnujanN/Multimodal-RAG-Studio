"""
Dense Vector Search Retriever.

Embeds user query using 512d CLIP text encoder and queries Qdrant cosine index.
"""
import logging
from typing import Any

from .base import BaseRetriever
from ..embeddings import embedder

logger = logging.getLogger(__name__)


class DenseRetriever(BaseRetriever):
    name = "dense"
    label = "Dense Vector Search (Cosine)"
    description = "Embeds query into 512d CLIP vector space and computes cosine similarity match against Qdrant index."

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        session_id: str | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        logger.info("Running Dense Vector Search for query: '%s' (limit=%d)", query[:50], limit)

        # 1. Embed query into 512d CLIP space
        query_vector = embedder.embed_text(query)

        # 2. Search Qdrant
        raw_results = self.qs.search_dense(
            query_vector=query_vector,
            limit=limit,
            session_id=session_id,
            user_id=self.user_id,
        )

        # 3. Format result
        formatted = []
        for r in raw_results:
            formatted.append({
                "text": r.get("text", ""),
                "source_type": r.get("source_type", "text"),
                "source_name": r.get("source_name", "document"),
                "score": round(r.get("_score", 0.0), 4),
                "metadata": r.get("metadata", {}),
            })

        logger.info("Dense retriever returned %d matches.", len(formatted))
        return formatted
